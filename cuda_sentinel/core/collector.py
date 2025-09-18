"""
GPU Data Collector - Main class for GPU monitoring using NVML

This module provides the core GPU monitoring functionality using NVIDIA's
Management Library (NVML) to collect real-time metrics and health data.
"""

import logging
import time
from typing import Optional, List, Dict, Any

# Try importing nvidia-ml-py first (preferred), fallback to pynvml
try:
    import nvidia_ml_py as nvml
except ImportError:
    try:
        import pynvml as nvml
    except ImportError:
        raise ImportError(
            "Neither nvidia-ml-py nor pynvml is available. "
            "Please install with: pip install nvidia-ml-py"
        )

from .models import GPUInfo, GPUMetrics, HealthStatus, HealthReport, BenchmarkResult
from .exceptions import NVMLError, GPUNotFoundError

logger = logging.getLogger(__name__)


class GPUCollector:
    """Main class for collecting GPU metrics using NVML"""
    
    def __init__(self):
        """Initialize NVML and discover GPUs"""
        try:
            nvml.nvmlInit()
            self.device_count = nvml.nvmlDeviceGetCount()
            logger.info(f"NVML initialized. {self.device_count} GPU(s) found.")
        except Exception as e:
            raise NVMLError(f"Failed to initialize NVML: {e}")
    
    def __del__(self):
        """Cleanup NVML on destruction"""
        try:
            nvml.nvmlShutdown()
        except:
            pass
    
    def get_gpu_info(self, gpu_index: int) -> GPUInfo:
        """Get basic GPU information"""
        if gpu_index >= self.device_count:
            raise GPUNotFoundError(gpu_index)
        
        try:
            handle = nvml.nvmlDeviceGetHandleByIndex(gpu_index)
            
            # Get basic info
            name = nvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            
            uuid = nvml.nvmlDeviceGetUUID(handle)
            if isinstance(uuid, bytes):
                uuid = uuid.decode('utf-8')
            
            # Driver version
            driver_version = nvml.nvmlSystemGetDriverVersion()
            if isinstance(driver_version, bytes):
                driver_version = driver_version.decode('utf-8')
            
            # CUDA version
            cuda_version = nvml.nvmlSystemGetCudaDriverVersion()
            cuda_major = cuda_version // 1000
            cuda_minor = (cuda_version % 1000) // 10
            cuda_version_str = f"{cuda_major}.{cuda_minor}"
            
            # Memory info
            memory_info = nvml.nvmlDeviceGetMemoryInfo(handle)
            memory_total_mb = memory_info.total // (1024 * 1024)
            
            # Compute capability
            major, minor = nvml.nvmlDeviceGetCudaComputeCapability(handle)
            compute_capability = f"{major}.{minor}"
            
            return GPUInfo(
                index=gpu_index,
                name=name,
                uuid=uuid,
                driver_version=driver_version,
                cuda_version=cuda_version_str,
                memory_total=memory_total_mb,
                compute_capability=compute_capability
            )
            
        except Exception as e:
            raise NVMLError(f"Failed to get GPU {gpu_index} info: {e}")
    
    def collect_metrics(self, gpu_index: int) -> GPUMetrics:
        """Collect real-time metrics for a GPU"""
        if gpu_index >= self.device_count:
            raise GPUNotFoundError(gpu_index)
        
        try:
            handle = nvml.nvmlDeviceGetHandleByIndex(gpu_index)
            metrics = GPUMetrics(gpu_index=gpu_index)
            
            # Temperature
            try:
                metrics.temperature_gpu = nvml.nvmlDeviceGetTemperature(
                    handle, nvml.NVML_TEMPERATURE_GPU
                )
            except:
                pass
            
            # Power
            try:
                metrics.power_draw = nvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
            except:
                pass
                
            try:
                metrics.power_limit = nvml.nvmlDeviceGetPowerManagementLimitConstraints(handle)[1] / 1000.0
            except:
                pass
            
            # Memory
            try:
                memory_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                metrics.memory_used = memory_info.used // (1024 * 1024)
                metrics.memory_free = memory_info.free // (1024 * 1024)
                metrics.memory_total = memory_info.total // (1024 * 1024)
                if metrics.memory_total > 0:
                    metrics.memory_utilization = (metrics.memory_used / metrics.memory_total) * 100
            except:
                pass
            
            # Utilization
            try:
                utilization = nvml.nvmlDeviceGetUtilizationRates(handle)
                metrics.gpu_utilization = utilization.gpu
                metrics.memory_utilization = utilization.memory
            except:
                pass
            
            # Clock speeds
            try:
                metrics.clock_graphics = nvml.nvmlDeviceGetClockInfo(
                    handle, nvml.NVML_CLOCK_GRAPHICS
                )
            except:
                pass
                
            try:
                metrics.clock_memory = nvml.nvmlDeviceGetClockInfo(
                    handle, nvml.NVML_CLOCK_MEM
                )
            except:
                pass
            
            # Fan speed
            try:
                metrics.fan_speed = nvml.nvmlDeviceGetFanSpeed(handle)
            except:
                pass
            
            # ECC errors
            try:
                ecc_corrected = nvml.nvmlDeviceGetTotalEccErrors(
                    handle, nvml.NVML_SINGLE_BIT_ECC, nvml.NVML_VOLATILE_ECC
                )
                metrics.ecc_errors_corrected = ecc_corrected
            except:
                pass
                
            try:
                ecc_uncorrected = nvml.nvmlDeviceGetTotalEccErrors(
                    handle, nvml.NVML_DOUBLE_BIT_ECC, nvml.NVML_VOLATILE_ECC
                )
                metrics.ecc_errors_uncorrected = ecc_uncorrected
            except:
                pass
            
            return metrics
            
        except Exception as e:
            raise NVMLError(f"Failed to collect metrics for GPU {gpu_index}: {e}")
    
    def get_advanced_metrics(self, gpu_index: int) -> Dict[str, Any]:
        """Get advanced GPU metrics not covered in basic collection"""
        if gpu_index >= self.device_count:
            raise GPUNotFoundError(gpu_index)
        
        try:
            handle = nvml.nvmlDeviceGetHandleByIndex(gpu_index)
            advanced_metrics = {}
            
            # PCIe information
            try:
                pcie_link_gen = nvml.nvmlDeviceGetMaxPcieLinkGeneration(handle)
                pcie_link_width = nvml.nvmlDeviceGetMaxPcieLinkWidth(handle)
                current_pcie_gen = nvml.nvmlDeviceGetCurrPcieLinkGeneration(handle)
                current_pcie_width = nvml.nvmlDeviceGetCurrPcieLinkWidth(handle)
                
                advanced_metrics.update({
                    'pcie_max_link_gen': pcie_link_gen,
                    'pcie_max_link_width': pcie_link_width,
                    'pcie_current_link_gen': current_pcie_gen,
                    'pcie_current_link_width': current_pcie_width,
                })
            except:
                pass
            
            # PCIe throughput
            try:
                pcie_tx = nvml.nvmlDeviceGetPcieThroughput(handle, nvml.NVML_PCIE_UTIL_TX_BYTES)
                pcie_rx = nvml.nvmlDeviceGetPcieThroughput(handle, nvml.NVML_PCIE_UTIL_RX_BYTES)
                advanced_metrics.update({
                    'pcie_tx_throughput': pcie_tx,
                    'pcie_rx_throughput': pcie_rx,
                })
            except:
                pass
            
            # PCIe replay counter
            try:
                pcie_replay = nvml.nvmlDeviceGetPcieReplayCounter(handle)
                advanced_metrics['pcie_replay_counter'] = pcie_replay
            except:
                pass
            
            # Performance state
            try:
                perf_state = nvml.nvmlDeviceGetPerformanceState(handle)
                advanced_metrics['performance_state'] = perf_state
            except:
                pass
            
            # Max clocks
            try:
                max_graphics_clock = nvml.nvmlDeviceGetMaxClockInfo(handle, nvml.NVML_CLOCK_GRAPHICS)
                max_memory_clock = nvml.nvmlDeviceGetMaxClockInfo(handle, nvml.NVML_CLOCK_MEM)
                max_sm_clock = nvml.nvmlDeviceGetMaxClockInfo(handle, nvml.NVML_CLOCK_SM)
                
                advanced_metrics.update({
                    'max_graphics_clock': max_graphics_clock,
                    'max_memory_clock': max_memory_clock,
                    'max_sm_clock': max_sm_clock,
                })
            except:
                pass
            
            # Temperature sensors
            try:
                # Memory temperature
                memory_temp = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_MEMORY)
                advanced_metrics['temperature_memory'] = memory_temp
            except:
                pass
            
            # Process information
            try:
                processes = nvml.nvmlDeviceGetComputeRunningProcesses(handle)
                advanced_metrics['process_count'] = len(processes)
                
                total_process_memory = 0
                for process in processes:
                    if hasattr(process, 'usedGpuMemory'):
                        total_process_memory += process.usedGpuMemory
                
                advanced_metrics['process_memory_used'] = total_process_memory // (1024 * 1024)  # MB
            except:
                advanced_metrics['process_count'] = 0
                advanced_metrics['process_memory_used'] = 0
            
            # Memory error information
            try:
                retired_pages_sbe = nvml.nvmlDeviceGetRetiredPages(handle, nvml.NVML_PAGE_RETIREMENT_CAUSE_MULTIPLE_SINGLE_BIT_ECC_ERRORS)
                retired_pages_dbe = nvml.nvmlDeviceGetRetiredPages(handle, nvml.NVML_PAGE_RETIREMENT_CAUSE_DOUBLE_BIT_ECC_ERROR)
                
                advanced_metrics.update({
                    'retired_pages_sbe': len(retired_pages_sbe) if retired_pages_sbe else 0,
                    'retired_pages_dbe': len(retired_pages_dbe) if retired_pages_dbe else 0,
                })
            except:
                pass
            
            # Detailed memory info
            try:
                memory_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                advanced_metrics.update({
                    'memory_reserved': getattr(memory_info, 'reserved', 0) // (1024 * 1024),  # MB
                })
            except:
                pass
            
            # Encoder/Decoder utilization
            try:
                encoder_util = nvml.nvmlDeviceGetEncoderUtilization(handle)
                decoder_util = nvml.nvmlDeviceGetDecoderUtilization(handle)
                
                advanced_metrics.update({
                    'encoder_utilization': encoder_util[0] if encoder_util else None,
                    'decoder_utilization': decoder_util[0] if decoder_util else None,
                })
            except:
                pass
            
            # Throttle reasons (detailed)
            try:
                throttle_reasons = nvml.nvmlDeviceGetCurrentClocksThrottleReasons(handle)
                
                # Using integer constants as fallback
                NVML_CLOCKS_THROTTLE_REASON_GPU_IDLE = 1
                NVML_CLOCKS_THROTTLE_REASON_APPLICATIONS_CLOCKS_SETTING = 2
                NVML_CLOCKS_THROTTLE_REASON_SW_POWER_CAP = 4
                NVML_CLOCKS_THROTTLE_REASON_HW_SLOWDOWN = 8
                NVML_CLOCKS_THROTTLE_REASON_SYNC_BOOST = 16
                NVML_CLOCKS_THROTTLE_REASON_SW_THERMAL_SLOWDOWN = 32
                NVML_CLOCKS_THROTTLE_REASON_HW_THERMAL_SLOWDOWN = 64
                NVML_CLOCKS_THROTTLE_REASON_HW_POWER_BRAKE_SLOWDOWN = 128
                
                advanced_metrics.update({
                    'throttle_gpu_idle': bool(throttle_reasons & NVML_CLOCKS_THROTTLE_REASON_GPU_IDLE),
                    'throttle_app_clocks': bool(throttle_reasons & NVML_CLOCKS_THROTTLE_REASON_APPLICATIONS_CLOCKS_SETTING),
                    'throttle_sw_power': bool(throttle_reasons & NVML_CLOCKS_THROTTLE_REASON_SW_POWER_CAP),
                    'throttle_hw_slowdown': bool(throttle_reasons & NVML_CLOCKS_THROTTLE_REASON_HW_SLOWDOWN),
                    'throttle_sync_boost': bool(throttle_reasons & NVML_CLOCKS_THROTTLE_REASON_SYNC_BOOST),
                    'throttle_sw_thermal': bool(throttle_reasons & NVML_CLOCKS_THROTTLE_REASON_SW_THERMAL_SLOWDOWN),
                    'throttle_hw_thermal': bool(throttle_reasons & NVML_CLOCKS_THROTTLE_REASON_HW_THERMAL_SLOWDOWN),
                    'throttle_hw_power': bool(throttle_reasons & NVML_CLOCKS_THROTTLE_REASON_HW_POWER_BRAKE_SLOWDOWN),
                })
            except:
                pass
            
            # GPU topology information
            try:
                # Multi-GPU systems için topology bilgisi
                for other_gpu in range(self.device_count):
                    if other_gpu != gpu_index:
                        try:
                            other_handle = nvml.nvmlDeviceGetHandleByIndex(other_gpu)
                            p2p_status = nvml.nvmlDeviceGetP2PStatus(handle, other_handle, nvml.NVML_P2P_CAPS_INDEX_READ)
                            advanced_metrics[f'p2p_link_to_gpu_{other_gpu}'] = p2p_status
                        except:
                            pass
            except:
                pass
            
            return advanced_metrics
            
        except Exception as e:
            logger.error(f"Failed to collect advanced metrics for GPU {gpu_index}: {e}")
            return {}
    
    def analyze_health(self, gpu_index: int) -> HealthReport:
        """Analyze GPU health based on current metrics"""
        metrics = self.collect_metrics(gpu_index)
        
        # Temperature analysis
        temp_status = HealthStatus.UNKNOWN
        temp_warnings = []
        
        if metrics.temperature_gpu is not None:
            if metrics.temperature_gpu < 70:
                temp_status = HealthStatus.HEALTHY
            elif metrics.temperature_gpu < 85:
                temp_status = HealthStatus.WARNING
                temp_warnings.append(f"GPU temperature is {metrics.temperature_gpu}°C (>70°C)")
            else:
                temp_status = HealthStatus.CRITICAL
                temp_warnings.append(f"GPU temperature is {metrics.temperature_gpu}°C (>85°C)")
        
        # Memory analysis
        memory_status = HealthStatus.UNKNOWN
        memory_warnings = []
        
        if metrics.memory_utilization is not None:
            if metrics.memory_utilization < 80:
                memory_status = HealthStatus.HEALTHY
            elif metrics.memory_utilization < 95:
                memory_status = HealthStatus.WARNING
                memory_warnings.append(f"Memory usage is {metrics.memory_utilization:.1f}% (>80%)")
            else:
                memory_status = HealthStatus.CRITICAL
                memory_warnings.append(f"Memory usage is {metrics.memory_utilization:.1f}% (>95%)")
        
        # Power analysis
        power_status = HealthStatus.UNKNOWN
        power_warnings = []
        
        if metrics.power_draw is not None and metrics.power_limit is not None:
            power_percent = (metrics.power_draw / metrics.power_limit) * 100
            if power_percent < 90:
                power_status = HealthStatus.HEALTHY
            elif power_percent < 98:
                power_status = HealthStatus.WARNING
                power_warnings.append(f"Power usage is {power_percent:.1f}% of limit")
            else:
                power_status = HealthStatus.CRITICAL
                power_warnings.append(f"Power usage is {power_percent:.1f}% of limit (>98%)")
        
        # Utilization analysis (informational)
        util_status = HealthStatus.HEALTHY
        
        # Overall status - worst of all individual statuses
        statuses = [temp_status, memory_status, power_status]
        if HealthStatus.CRITICAL in statuses:
            overall_status = HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            overall_status = HealthStatus.WARNING
        elif HealthStatus.HEALTHY in statuses:
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.UNKNOWN
        
        # Compile all warnings
        all_warnings = temp_warnings + memory_warnings + power_warnings
        
        # Generate recommendations
        recommendations = []
        if temp_status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
            recommendations.append("Check GPU cooling and case ventilation")
        if memory_status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
            recommendations.append("Consider reducing GPU memory usage")
        if power_status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
            recommendations.append("Check power supply capacity")
        
        return HealthReport(
            gpu_index=gpu_index,
            overall_status=overall_status,
            temperature_status=temp_status,
            memory_status=memory_status,
            power_status=power_status,
            utilization_status=util_status,
            warnings=all_warnings,
            recommendations=recommendations,
            current_metrics=metrics
        )
    
    def run_simple_benchmark(self, gpu_index: int) -> BenchmarkResult:
        """Run a simple benchmark test"""
        start_time = time.time()
        
        try:
            # Simple benchmark - just measure basic operations
            import numpy as np
            
            # Generate test data
            size = 1000
            data = np.random.random((size, size)).astype(np.float32)
            
            # Simulate computation
            result = np.dot(data, data.T)
            duration = time.time() - start_time
            
            # Estimate GFLOPS (very rough)
            operations = 2 * size ** 3  # Matrix multiplication ops
            gflops = (operations / duration) / 1e9
            
            return BenchmarkResult(
                test_name="simple_matrix_multiply",
                gpu_index=gpu_index,
                duration=duration,
                gflops=gflops,
                success=True,
                metadata={"matrix_size": size, "data_type": "float32"}
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return BenchmarkResult(
                test_name="simple_matrix_multiply",
                gpu_index=gpu_index,
                duration=duration,
                success=False,
                error_message=str(e)
            )
