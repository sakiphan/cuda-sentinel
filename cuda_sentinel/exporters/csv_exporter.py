"""
CSV Exporter - Export GPU metrics in CSV format

This module provides CSV export functionality for GPU metrics data.
"""

import csv
import io
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..core.collector import GPUCollector

logger = logging.getLogger(__name__)


class CSVExporter:
    """CSV exporter for GPU metrics"""
    
    def __init__(self, collector: GPUCollector):
        self.collector = collector
    
    def export_metrics_csv(self, gpu_indices: Optional[List[int]] = None) -> str:
        """Export GPU metrics as CSV"""
        if gpu_indices is None:
            gpu_indices = list(range(self.collector.device_count))
        
        output = io.StringIO()
        
        # Define CSV headers
        headers = [
            'timestamp', 'gpu_index', 'gpu_name', 'gpu_uuid',
            'temperature_gpu', 'temperature_memory',
            'power_draw', 'power_limit',
            'memory_used_mb', 'memory_free_mb', 'memory_total_mb', 'memory_utilization_percent',
            'gpu_utilization_percent', 'memory_utilization_percent',
            'encoder_utilization_percent', 'decoder_utilization_percent',
            'fan_speed_percent',
            'clock_graphics_mhz', 'clock_memory_mhz', 'clock_sm_mhz',
            'ecc_errors_corrected', 'ecc_errors_uncorrected'
        ]
        
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        
        # Collect data for each GPU
        for gpu_index in gpu_indices:
            try:
                gpu_info = self.collector.get_gpu_info(gpu_index)
                metrics = self.collector.collect_metrics(gpu_index)
                
                row = {
                    'timestamp': metrics.timestamp.isoformat(),
                    'gpu_index': gpu_index,
                    'gpu_name': gpu_info.name,
                    'gpu_uuid': gpu_info.uuid,
                    'temperature_gpu': metrics.temperature_gpu,
                    'temperature_memory': metrics.temperature_memory,
                    'power_draw': metrics.power_draw,
                    'power_limit': metrics.power_limit,
                    'memory_used_mb': metrics.memory_used,
                    'memory_free_mb': metrics.memory_free,
                    'memory_total_mb': metrics.memory_total,
                    'memory_utilization_percent': metrics.memory_utilization,
                    'gpu_utilization_percent': metrics.gpu_utilization,
                    'memory_utilization_percent': metrics.memory_utilization,
                    'encoder_utilization_percent': metrics.encoder_utilization,
                    'decoder_utilization_percent': metrics.decoder_utilization,
                    'fan_speed_percent': metrics.fan_speed,
                    'clock_graphics_mhz': metrics.clock_graphics,
                    'clock_memory_mhz': metrics.clock_memory,
                    'clock_sm_mhz': metrics.clock_sm,
                    'ecc_errors_corrected': metrics.ecc_errors_corrected,
                    'ecc_errors_uncorrected': metrics.ecc_errors_uncorrected
                }
                
                # Convert None values to empty strings for CSV
                row = {k: (v if v is not None else '') for k, v in row.items()}
                
                writer.writerow(row)
                
            except Exception as e:
                logger.error(f"Error collecting data for GPU {gpu_index}: {e}")
                # Write error row
                error_row = {header: '' for header in headers}
                error_row.update({
                    'timestamp': datetime.now().isoformat(),
                    'gpu_index': gpu_index,
                    'gpu_name': f'ERROR: {str(e)}'
                })
                writer.writerow(error_row)
        
        return output.getvalue()
    
    def export_health_csv(self, gpu_indices: Optional[List[int]] = None) -> str:
        """Export GPU health data as CSV"""
        if gpu_indices is None:
            gpu_indices = list(range(self.collector.device_count))
        
        output = io.StringIO()
        
        headers = [
            'timestamp', 'gpu_index', 'gpu_name',
            'overall_status', 'temperature_status', 'memory_status', 
            'power_status', 'utilization_status',
            'warnings', 'recommendations'
        ]
        
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        
        for gpu_index in gpu_indices:
            try:
                gpu_info = self.collector.get_gpu_info(gpu_index)
                health_report = self.collector.analyze_health(gpu_index)
                
                row = {
                    'timestamp': health_report.timestamp.isoformat(),
                    'gpu_index': gpu_index,
                    'gpu_name': gpu_info.name,
                    'overall_status': health_report.overall_status.value,
                    'temperature_status': health_report.temperature_status.value,
                    'memory_status': health_report.memory_status.value,
                    'power_status': health_report.power_status.value,
                    'utilization_status': health_report.utilization_status.value,
                    'warnings': '; '.join(health_report.warnings) if health_report.warnings else '',
                    'recommendations': '; '.join(health_report.recommendations) if health_report.recommendations else ''
                }
                
                writer.writerow(row)
                
            except Exception as e:
                logger.error(f"Error analyzing health for GPU {gpu_index}: {e}")
                error_row = {header: '' for header in headers}
                error_row.update({
                    'timestamp': datetime.now().isoformat(),
                    'gpu_index': gpu_index,
                    'gpu_name': f'ERROR: {str(e)}',
                    'overall_status': 'error'
                })
                writer.writerow(error_row)
        
        return output.getvalue()
    
    def export_benchmark_csv(self, gpu_indices: Optional[List[int]] = None) -> str:
        """Export benchmark results as CSV"""
        if gpu_indices is None:
            gpu_indices = list(range(self.collector.device_count))
        
        output = io.StringIO()
        
        headers = [
            'timestamp', 'gpu_index', 'gpu_name', 'test_name',
            'duration_seconds', 'gflops', 'memory_bandwidth_gbps',
            'success', 'error_message'
        ]
        
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        
        for gpu_index in gpu_indices:
            try:
                gpu_info = self.collector.get_gpu_info(gpu_index)
                benchmark_result = self.collector.run_simple_benchmark(gpu_index)
                
                row = {
                    'timestamp': benchmark_result.timestamp.isoformat(),
                    'gpu_index': gpu_index,
                    'gpu_name': gpu_info.name,
                    'test_name': benchmark_result.test_name,
                    'duration_seconds': benchmark_result.duration,
                    'gflops': benchmark_result.gflops if benchmark_result.gflops else '',
                    'memory_bandwidth_gbps': benchmark_result.memory_bandwidth if benchmark_result.memory_bandwidth else '',
                    'success': benchmark_result.success,
                    'error_message': benchmark_result.error_message if benchmark_result.error_message else ''
                }
                
                writer.writerow(row)
                
            except Exception as e:
                logger.error(f"Error running benchmark for GPU {gpu_index}: {e}")
                error_row = {header: '' for header in headers}
                error_row.update({
                    'timestamp': datetime.now().isoformat(),
                    'gpu_index': gpu_index,
                    'gpu_name': 'ERROR',
                    'test_name': 'error',
                    'success': False,
                    'error_message': str(e)
                })
                writer.writerow(error_row)
        
        return output.getvalue()
    
    def export_system_info_csv(self) -> str:
        """Export system and GPU information as CSV"""
        output = io.StringIO()
        
        headers = [
            'gpu_index', 'name', 'uuid', 'driver_version', 'cuda_version',
            'memory_total_mb', 'compute_capability'
        ]
        
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        
        for gpu_index in range(self.collector.device_count):
            try:
                gpu_info = self.collector.get_gpu_info(gpu_index)
                
                row = {
                    'gpu_index': gpu_index,
                    'name': gpu_info.name,
                    'uuid': gpu_info.uuid,
                    'driver_version': gpu_info.driver_version,
                    'cuda_version': gpu_info.cuda_version,
                    'memory_total_mb': gpu_info.memory_total,
                    'compute_capability': gpu_info.compute_capability
                }
                
                writer.writerow(row)
                
            except Exception as e:
                logger.error(f"Error getting info for GPU {gpu_index}: {e}")
                error_row = {header: '' for header in headers}
                error_row.update({
                    'gpu_index': gpu_index,
                    'name': f'ERROR: {str(e)}'
                })
                writer.writerow(error_row)
        
        return output.getvalue()
