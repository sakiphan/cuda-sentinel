"""
Prometheus Exporter - Export GPU metrics in Prometheus format

This module provides a comprehensive Prometheus metrics exporter that
collects and exposes GPU metrics for monitoring and alerting.
"""

import time
import logging
from typing import Dict, List, Optional
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily

from ..core.collector import GPUCollector
from ..core.models import GPUMetrics, HealthStatus

logger = logging.getLogger(__name__)


class PrometheusExporter:
    """Prometheus metrics exporter for GPU data"""
    
    def __init__(self, collector: GPUCollector, registry: Optional[CollectorRegistry] = None):
        self.collector = collector
        self.registry = registry or CollectorRegistry()
        
        # Initialize metrics
        self._setup_metrics()
        
        # Register custom collector
        self.registry.register(self)
    
    def _setup_metrics(self):
        """Set up Prometheus metrics"""
        
        # Basic GPU metrics
        self.gpu_temperature = Gauge(
            'cuda_sentinel_gpu_temperature_celsius',
            'GPU temperature in Celsius',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_power_draw = Gauge(
            'cuda_sentinel_gpu_power_draw_watts',
            'GPU power consumption in watts',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_power_limit = Gauge(
            'cuda_sentinel_gpu_power_limit_watts',
            'GPU power limit in watts',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_memory_used = Gauge(
            'cuda_sentinel_gpu_memory_used_bytes',
            'GPU memory used in bytes',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_memory_total = Gauge(
            'cuda_sentinel_gpu_memory_total_bytes',
            'GPU total memory in bytes',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_memory_free = Gauge(
            'cuda_sentinel_gpu_memory_free_bytes',
            'GPU free memory in bytes',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_utilization = Gauge(
            'cuda_sentinel_gpu_utilization_percent',
            'GPU utilization percentage',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_memory_utilization = Gauge(
            'cuda_sentinel_gpu_memory_utilization_percent',
            'GPU memory utilization percentage',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # Clock speeds
        self.gpu_clock_graphics = Gauge(
            'cuda_sentinel_gpu_clock_graphics_mhz',
            'GPU graphics clock in MHz',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_clock_memory = Gauge(
            'cuda_sentinel_gpu_clock_memory_mhz',
            'GPU memory clock in MHz',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_clock_sm = Gauge(
            'cuda_sentinel_gpu_clock_sm_mhz',
            'GPU SM clock in MHz',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # Fan speed
        self.gpu_fan_speed = Gauge(
            'cuda_sentinel_gpu_fan_speed_percent',
            'GPU fan speed percentage',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # ECC errors
        self.gpu_ecc_errors_corrected = Counter(
            'cuda_sentinel_gpu_ecc_errors_corrected_total',
            'Total corrected ECC errors',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_ecc_errors_uncorrected = Counter(
            'cuda_sentinel_gpu_ecc_errors_uncorrected_total',
            'Total uncorrected ECC errors',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # Health status
        self.gpu_health_status = Gauge(
            'cuda_sentinel_gpu_health_status',
            'GPU health status (0=unknown, 1=healthy, 2=warning, 3=critical)',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # Benchmark metrics
        self.benchmark_gflops = Gauge(
            'cuda_sentinel_benchmark_gflops',
            'Benchmark GFLOPS performance',
            ['gpu', 'gpu_name', 'test_name'],
            registry=self.registry
        )
        
        self.benchmark_memory_bandwidth = Gauge(
            'cuda_sentinel_benchmark_memory_bandwidth_gbps',
            'Benchmark memory bandwidth in GB/s',
            ['gpu', 'gpu_name', 'test_name'],
            registry=self.registry
        )
        
        self.benchmark_duration = Gauge(
            'cuda_sentinel_benchmark_duration_seconds',
            'Benchmark duration in seconds',
            ['gpu', 'gpu_name', 'test_name'],
            registry=self.registry
        )
        
        # Scrape metrics
        self.scrape_duration = Histogram(
            'cuda_sentinel_scrape_duration_seconds',
            'Time spent scraping GPU metrics',
            registry=self.registry
        )
        
        self.last_scrape_timestamp = Gauge(
            'cuda_sentinel_last_scrape_timestamp',
            'Timestamp of last successful scrape',
            registry=self.registry
        )
        
        # Advanced PCIe metrics
        self.gpu_pcie_max_link_gen = Gauge(
            'cuda_sentinel_gpu_pcie_max_link_generation',
            'Maximum PCIe link generation',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_pcie_max_link_width = Gauge(
            'cuda_sentinel_gpu_pcie_max_link_width',
            'Maximum PCIe link width',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_pcie_current_link_gen = Gauge(
            'cuda_sentinel_gpu_pcie_current_link_generation',
            'Current PCIe link generation',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_pcie_current_link_width = Gauge(
            'cuda_sentinel_gpu_pcie_current_link_width',
            'Current PCIe link width',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_pcie_tx_throughput = Gauge(
            'cuda_sentinel_gpu_pcie_tx_throughput_kbps',
            'PCIe TX throughput in KB/s',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_pcie_rx_throughput = Gauge(
            'cuda_sentinel_gpu_pcie_rx_throughput_kbps',
            'PCIe RX throughput in KB/s',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_pcie_replay_counter = Counter(
            'cuda_sentinel_gpu_pcie_replay_counter_total',
            'PCIe replay counter',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # Performance state
        self.gpu_performance_state = Gauge(
            'cuda_sentinel_gpu_performance_state',
            'GPU performance state (P-state)',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # Maximum clocks
        self.gpu_max_graphics_clock = Gauge(
            'cuda_sentinel_gpu_max_graphics_clock_mhz',
            'Maximum graphics clock in MHz',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_max_memory_clock = Gauge(
            'cuda_sentinel_gpu_max_memory_clock_mhz',
            'Maximum memory clock in MHz',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_max_sm_clock = Gauge(
            'cuda_sentinel_gpu_max_sm_clock_mhz',
            'Maximum SM clock in MHz',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # Memory temperature
        self.gpu_memory_temperature = Gauge(
            'cuda_sentinel_gpu_memory_temperature_celsius',
            'GPU memory temperature in Celsius',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # Process information
        self.gpu_process_count = Gauge(
            'cuda_sentinel_gpu_process_count',
            'Number of processes running on GPU',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_process_memory_used = Gauge(
            'cuda_sentinel_gpu_process_memory_used_bytes',
            'Memory used by processes in bytes',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # Retired pages
        self.gpu_retired_pages_sbe = Gauge(
            'cuda_sentinel_gpu_retired_pages_sbe',
            'Retired pages due to single bit ECC errors',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_retired_pages_dbe = Gauge(
            'cuda_sentinel_gpu_retired_pages_dbe',
            'Retired pages due to double bit ECC errors',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # Memory reserved
        self.gpu_memory_reserved = Gauge(
            'cuda_sentinel_gpu_memory_reserved_bytes',
            'Reserved GPU memory in bytes',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # Encoder/Decoder utilization
        self.gpu_encoder_utilization = Gauge(
            'cuda_sentinel_gpu_encoder_utilization_percent',
            'GPU encoder utilization percentage',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_decoder_utilization = Gauge(
            'cuda_sentinel_gpu_decoder_utilization_percent',
            'GPU decoder utilization percentage',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # Detailed throttle reasons
        self.gpu_throttle_idle = Gauge(
            'cuda_sentinel_gpu_throttle_idle',
            'GPU throttled due to idle state',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_throttle_app_clocks = Gauge(
            'cuda_sentinel_gpu_throttle_app_clocks',
            'GPU throttled due to application clocks setting',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_throttle_sw_power = Gauge(
            'cuda_sentinel_gpu_throttle_sw_power',
            'GPU throttled due to software power cap',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_throttle_hw_slowdown = Gauge(
            'cuda_sentinel_gpu_throttle_hw_slowdown',
            'GPU throttled due to hardware slowdown',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_throttle_sync_boost = Gauge(
            'cuda_sentinel_gpu_throttle_sync_boost',
            'GPU throttled due to sync boost',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_throttle_sw_thermal = Gauge(
            'cuda_sentinel_gpu_throttle_sw_thermal',
            'GPU throttled due to software thermal slowdown',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_throttle_hw_thermal = Gauge(
            'cuda_sentinel_gpu_throttle_hw_thermal',
            'GPU throttled due to hardware thermal slowdown',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        self.gpu_throttle_hw_power = Gauge(
            'cuda_sentinel_gpu_throttle_hw_power',
            'GPU throttled due to hardware power brake',
            ['gpu', 'gpu_name', 'uuid'],
            registry=self.registry
        )
        
        # P2P connectivity
        self.gpu_p2p_link = Gauge(
            'cuda_sentinel_gpu_p2p_link_status',
            'P2P link status between GPUs',
            ['gpu', 'gpu_name', 'uuid', 'target_gpu'],
            registry=self.registry
        )
    
    def collect(self):
        """Collect metrics for Prometheus (called by prometheus_client)"""
        start_time = time.time()
        
        try:
            # Collect data for all GPUs
            for gpu_index in range(self.collector.device_count):
                self._collect_gpu_metrics(gpu_index)
            
            # Update scrape metrics
            scrape_duration = time.time() - start_time
            self.scrape_duration.observe(scrape_duration)
            self.last_scrape_timestamp.set(time.time())
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
        
        # Return empty list since we're using the registry approach
        return []
    
    def _collect_gpu_metrics(self, gpu_index: int):
        """Collect metrics for a specific GPU"""
        try:
            # Get GPU info and metrics
            gpu_info = self.collector.get_gpu_info(gpu_index)
            metrics = self.collector.collect_metrics(gpu_index)
            health_report = self.collector.analyze_health(gpu_index)
            advanced_metrics = self.collector.get_advanced_metrics(gpu_index)
            
            labels = [str(gpu_index), gpu_info.name, gpu_info.uuid]
            
            # Temperature
            if metrics.temperature_gpu is not None:
                self.gpu_temperature.labels(*labels).set(metrics.temperature_gpu)
            
            # Power
            if metrics.power_draw is not None:
                self.gpu_power_draw.labels(*labels).set(metrics.power_draw)
            if metrics.power_limit is not None:
                self.gpu_power_limit.labels(*labels).set(metrics.power_limit)
            
            # Memory
            if metrics.memory_used is not None:
                self.gpu_memory_used.labels(*labels).set(metrics.memory_used * 1024 * 1024)  # Convert MB to bytes
            if metrics.memory_total is not None:
                self.gpu_memory_total.labels(*labels).set(metrics.memory_total * 1024 * 1024)
            if metrics.memory_free is not None:
                self.gpu_memory_free.labels(*labels).set(metrics.memory_free * 1024 * 1024)
            
            # Utilization
            if metrics.gpu_utilization is not None:
                self.gpu_utilization.labels(*labels).set(metrics.gpu_utilization)
            if metrics.memory_utilization is not None:
                self.gpu_memory_utilization.labels(*labels).set(metrics.memory_utilization)
            
            # Clock speeds
            if metrics.clock_graphics is not None:
                self.gpu_clock_graphics.labels(*labels).set(metrics.clock_graphics)
            if metrics.clock_memory is not None:
                self.gpu_clock_memory.labels(*labels).set(metrics.clock_memory)
            if metrics.clock_sm is not None:
                self.gpu_clock_sm.labels(*labels).set(metrics.clock_sm)
            
            # Fan speed
            if metrics.fan_speed is not None:
                self.gpu_fan_speed.labels(*labels).set(metrics.fan_speed)
            
            # ECC errors
            if metrics.ecc_errors_corrected is not None:
                self.gpu_ecc_errors_corrected.labels(*labels)._value._value = metrics.ecc_errors_corrected
            if metrics.ecc_errors_uncorrected is not None:
                self.gpu_ecc_errors_uncorrected.labels(*labels)._value._value = metrics.ecc_errors_uncorrected
            
            # Health status
            health_value = self._health_status_to_number(health_report.overall_status)
            self.gpu_health_status.labels(*labels).set(health_value)
            
            # Advanced metrics
            if advanced_metrics:
                # PCIe information
                if 'pcie_max_link_gen' in advanced_metrics:
                    self.gpu_pcie_max_link_gen.labels(*labels).set(advanced_metrics['pcie_max_link_gen'])
                if 'pcie_max_link_width' in advanced_metrics:
                    self.gpu_pcie_max_link_width.labels(*labels).set(advanced_metrics['pcie_max_link_width'])
                if 'pcie_current_link_gen' in advanced_metrics:
                    self.gpu_pcie_current_link_gen.labels(*labels).set(advanced_metrics['pcie_current_link_gen'])
                if 'pcie_current_link_width' in advanced_metrics:
                    self.gpu_pcie_current_link_width.labels(*labels).set(advanced_metrics['pcie_current_link_width'])
                
                # PCIe throughput
                if 'pcie_tx_throughput' in advanced_metrics:
                    self.gpu_pcie_tx_throughput.labels(*labels).set(advanced_metrics['pcie_tx_throughput'])
                if 'pcie_rx_throughput' in advanced_metrics:
                    self.gpu_pcie_rx_throughput.labels(*labels).set(advanced_metrics['pcie_rx_throughput'])
                
                # PCIe replay counter
                if 'pcie_replay_counter' in advanced_metrics:
                    self.gpu_pcie_replay_counter.labels(*labels)._value._value = advanced_metrics['pcie_replay_counter']
                
                # Performance state
                if 'performance_state' in advanced_metrics:
                    self.gpu_performance_state.labels(*labels).set(advanced_metrics['performance_state'])
                
                # Maximum clocks
                if 'max_graphics_clock' in advanced_metrics:
                    self.gpu_max_graphics_clock.labels(*labels).set(advanced_metrics['max_graphics_clock'])
                if 'max_memory_clock' in advanced_metrics:
                    self.gpu_max_memory_clock.labels(*labels).set(advanced_metrics['max_memory_clock'])
                if 'max_sm_clock' in advanced_metrics:
                    self.gpu_max_sm_clock.labels(*labels).set(advanced_metrics['max_sm_clock'])
                
                # Memory temperature
                if 'temperature_memory' in advanced_metrics:
                    self.gpu_memory_temperature.labels(*labels).set(advanced_metrics['temperature_memory'])
                
                # Process information
                if 'process_count' in advanced_metrics:
                    self.gpu_process_count.labels(*labels).set(advanced_metrics['process_count'])
                if 'process_memory_used' in advanced_metrics:
                    self.gpu_process_memory_used.labels(*labels).set(advanced_metrics['process_memory_used'] * 1024 * 1024)  # Convert MB to bytes
                
                # Retired pages
                if 'retired_pages_sbe' in advanced_metrics:
                    self.gpu_retired_pages_sbe.labels(*labels).set(advanced_metrics['retired_pages_sbe'])
                if 'retired_pages_dbe' in advanced_metrics:
                    self.gpu_retired_pages_dbe.labels(*labels).set(advanced_metrics['retired_pages_dbe'])
                
                # Memory reserved
                if 'memory_reserved' in advanced_metrics:
                    self.gpu_memory_reserved.labels(*labels).set(advanced_metrics['memory_reserved'] * 1024 * 1024)  # Convert MB to bytes
                
                # Encoder/Decoder utilization
                if 'encoder_utilization' in advanced_metrics and advanced_metrics['encoder_utilization'] is not None:
                    self.gpu_encoder_utilization.labels(*labels).set(advanced_metrics['encoder_utilization'])
                if 'decoder_utilization' in advanced_metrics and advanced_metrics['decoder_utilization'] is not None:
                    self.gpu_decoder_utilization.labels(*labels).set(advanced_metrics['decoder_utilization'])
                
                # Detailed throttle reasons
                throttle_metrics = {
                    'throttle_gpu_idle': self.gpu_throttle_idle,
                    'throttle_app_clocks': self.gpu_throttle_app_clocks,
                    'throttle_sw_power': self.gpu_throttle_sw_power,
                    'throttle_hw_slowdown': self.gpu_throttle_hw_slowdown,
                    'throttle_sync_boost': self.gpu_throttle_sync_boost,
                    'throttle_sw_thermal': self.gpu_throttle_sw_thermal,
                    'throttle_hw_thermal': self.gpu_throttle_hw_thermal,
                    'throttle_hw_power': self.gpu_throttle_hw_power,
                }
                
                for throttle_key, throttle_metric in throttle_metrics.items():
                    if throttle_key in advanced_metrics:
                        throttle_metric.labels(*labels).set(1 if advanced_metrics[throttle_key] else 0)
                
                # P2P connectivity
                for key, value in advanced_metrics.items():
                    if key.startswith('p2p_link_to_gpu_'):
                        target_gpu = key.split('_')[-1]
                        p2p_labels = labels + [target_gpu]
                        self.gpu_p2p_link.labels(*p2p_labels).set(1 if value else 0)
            
            # Run benchmark and update metrics
            try:
                benchmark_result = self.collector.run_simple_benchmark(gpu_index)
                benchmark_labels = [str(gpu_index), gpu_info.name, benchmark_result.test_name]
                
                if benchmark_result.success and benchmark_result.gflops:
                    self.benchmark_gflops.labels(*benchmark_labels).set(benchmark_result.gflops)
                if benchmark_result.success and benchmark_result.memory_bandwidth:
                    self.benchmark_memory_bandwidth.labels(*benchmark_labels).set(benchmark_result.memory_bandwidth)
                if benchmark_result.duration:
                    self.benchmark_duration.labels(*benchmark_labels).set(benchmark_result.duration)
                    
            except Exception as e:
                logger.warning(f"Benchmark failed for GPU {gpu_index}: {e}")
            
        except Exception as e:
            logger.error(f"Error collecting metrics for GPU {gpu_index}: {e}")
    
    def _health_status_to_number(self, status: HealthStatus) -> int:
        """Convert health status to numeric value"""
        mapping = {
            HealthStatus.UNKNOWN: 0,
            HealthStatus.HEALTHY: 1,
            HealthStatus.WARNING: 2,
            HealthStatus.CRITICAL: 3
        }
        return mapping.get(status, 0)
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        self.collect()
        return generate_latest(self.registry)
    
    def get_content_type(self) -> str:
        """Get the content type for Prometheus metrics"""
        return CONTENT_TYPE_LATEST
