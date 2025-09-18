"""
JSON Exporter - Export GPU metrics in JSON format

This module provides JSON export functionality for GPU metrics and health data.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..core.collector import GPUCollector
from ..core.models import GPUInfo, GPUMetrics, HealthReport

logger = logging.getLogger(__name__)


class JSONExporter:
    """JSON exporter for GPU metrics"""
    
    def __init__(self, collector: GPUCollector):
        self.collector = collector
    
    def export_all_gpus(self, include_health: bool = True, include_benchmark: bool = False) -> str:
        """Export all GPU data as JSON"""
        data = []
        
        for gpu_index in range(self.collector.device_count):
            gpu_data = self.export_gpu(gpu_index, include_health, include_benchmark)
            data.append(gpu_data)
        
        return json.dumps(data, indent=2, default=self._json_serializer)
    
    def export_gpu(self, gpu_index: int, include_health: bool = True, include_benchmark: bool = False) -> Dict[str, Any]:
        """Export specific GPU data"""
        try:
            gpu_info = self.collector.get_gpu_info(gpu_index)
            metrics = self.collector.collect_metrics(gpu_index)
            
            result = {
                "gpu_info": gpu_info.dict(),
                "metrics": metrics.dict(),
                "timestamp": datetime.now().isoformat()
            }
            
            if include_health:
                health_report = self.collector.analyze_health(gpu_index)
                result["health"] = health_report.dict()
            
            if include_benchmark:
                try:
                    benchmark_result = self.collector.run_simple_benchmark(gpu_index)
                    result["benchmark"] = benchmark_result.dict()
                except Exception as e:
                    logger.warning(f"Benchmark failed for GPU {gpu_index}: {e}")
                    result["benchmark"] = {"error": str(e)}
            
            return result
            
        except Exception as e:
            logger.error(f"Error exporting GPU {gpu_index}: {e}")
            return {
                "gpu_index": gpu_index,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def export_metrics_only(self, gpu_indices: Optional[List[int]] = None) -> str:
        """Export only metrics data (lightweight)"""
        if gpu_indices is None:
            gpu_indices = list(range(self.collector.device_count))
        
        data = []
        for gpu_index in gpu_indices:
            try:
                gpu_info = self.collector.get_gpu_info(gpu_index)
                metrics = self.collector.collect_metrics(gpu_index)
                
                # Flatten data for simpler structure
                flattened = {
                    "gpu_index": gpu_index,
                    "gpu_name": gpu_info.name,
                    "gpu_uuid": gpu_info.uuid,
                    "timestamp": metrics.timestamp.isoformat(),
                    **{k: v for k, v in metrics.dict().items() if k not in ['gpu_index', 'timestamp']}
                }
                
                data.append(flattened)
                
            except Exception as e:
                logger.error(f"Error collecting metrics for GPU {gpu_index}: {e}")
                data.append({
                    "gpu_index": gpu_index,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return json.dumps(data, indent=2, default=self._json_serializer)
    
    def export_health_summary(self) -> str:
        """Export health summary for all GPUs"""
        data = {
            "summary": {
                "total_gpus": self.collector.device_count,
                "healthy_count": 0,
                "warning_count": 0,
                "critical_count": 0,
                "unknown_count": 0
            },
            "gpus": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for gpu_index in range(self.collector.device_count):
            try:
                gpu_info = self.collector.get_gpu_info(gpu_index)
                health_report = self.collector.analyze_health(gpu_index)
                
                gpu_health = {
                    "gpu_index": gpu_index,
                    "gpu_name": gpu_info.name,
                    "status": health_report.overall_status.value,
                    "warnings": health_report.warnings,
                    "recommendations": health_report.recommendations
                }
                
                data["gpus"].append(gpu_health)
                
                # Update counters
                status = health_report.overall_status.value
                if status == "healthy":
                    data["summary"]["healthy_count"] += 1
                elif status == "warning":
                    data["summary"]["warning_count"] += 1
                elif status == "critical":
                    data["summary"]["critical_count"] += 1
                else:
                    data["summary"]["unknown_count"] += 1
                    
            except Exception as e:
                logger.error(f"Error analyzing health for GPU {gpu_index}: {e}")
                data["gpus"].append({
                    "gpu_index": gpu_index,
                    "status": "error",
                    "error": str(e)
                })
                data["summary"]["unknown_count"] += 1
        
        return json.dumps(data, indent=2, default=self._json_serializer)
    
    def export_system_info(self) -> str:
        """Export system and GPU information"""
        data = {
            "system": {
                "gpu_count": self.collector.device_count,
                "timestamp": datetime.now().isoformat()
            },
            "gpus": []
        }
        
        for gpu_index in range(self.collector.device_count):
            try:
                gpu_info = self.collector.get_gpu_info(gpu_index)
                data["gpus"].append(gpu_info.dict())
            except Exception as e:
                logger.error(f"Error getting info for GPU {gpu_index}: {e}")
                data["gpus"].append({
                    "index": gpu_index,
                    "error": str(e)
                })
        
        return json.dumps(data, indent=2, default=self._json_serializer)
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for non-standard types"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'dict'):
            return obj.dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
