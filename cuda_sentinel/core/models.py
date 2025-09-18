"""
Data models - Pydantic models for GPU metrics and information
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """GPU health status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class GPUInfo(BaseModel):
    """Basic GPU information"""
    index: int = Field(..., description="GPU index")
    name: str = Field(..., description="GPU model")
    uuid: str = Field(..., description="GPU UUID")
    driver_version: str = Field(..., description="Driver version")
    cuda_version: str = Field(..., description="CUDA version")
    memory_total: int = Field(..., description="Total memory (MB)")
    compute_capability: str = Field(..., description="Compute capability")
    
    class Config:
        json_schema_extra = {
            "example": {
                "index": 0,
                "name": "NVIDIA GeForce RTX 4090",
                "uuid": "GPU-12345678-1234-1234-1234-123456789abc",
                "driver_version": "525.60.11",
                "cuda_version": "12.0",
                "memory_total": 24564,
                "compute_capability": "8.9"
            }
        }


class GPUMetrics(BaseModel):
    """Real-time GPU metrics"""
    gpu_index: int = Field(..., description="GPU index")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Temperature metrics
    temperature_gpu: Optional[float] = Field(None, description="GPU temperature (°C)")
    temperature_memory: Optional[float] = Field(None, description="Memory temperature (°C)")
    
    # Power metrics
    power_draw: Optional[float] = Field(None, description="Power consumption (W)")
    power_limit: Optional[float] = Field(None, description="Power limit (W)")
    
    # Memory metrics
    memory_used: Optional[int] = Field(None, description="Used memory (MB)")
    memory_free: Optional[int] = Field(None, description="Free memory (MB)")
    memory_total: Optional[int] = Field(None, description="Total memory (MB)")
    memory_utilization: Optional[float] = Field(None, description="Memory utilization (%)")
    
    # Utilization metrics
    gpu_utilization: Optional[float] = Field(None, description="GPU utilization (%)")
    encoder_utilization: Optional[float] = Field(None, description="Encoder utilization (%)")
    decoder_utilization: Optional[float] = Field(None, description="Decoder utilization (%)")
    
    # Fan metrics
    fan_speed: Optional[float] = Field(None, description="Fan speed (%)")
    
    # Clock metrics
    clock_graphics: Optional[int] = Field(None, description="Graphics clock (MHz)")
    clock_memory: Optional[int] = Field(None, description="Memory clock (MHz)")
    clock_sm: Optional[int] = Field(None, description="SM clock (MHz)")
    
    # ECC error metrics
    ecc_errors_corrected: Optional[int] = Field(None, description="Corrected ECC errors")
    ecc_errors_uncorrected: Optional[int] = Field(None, description="Uncorrected ECC errors")
    
    # Throttle reasons
    throttle_reasons: Optional[Dict[str, bool]] = Field(None, description="Throttle reasons")
    
    class Config:
        json_schema_extra = {
            "example": {
                "gpu_index": 0,
                "timestamp": "2025-09-18T10:30:00",
                "temperature_gpu": 72.0,
                "power_draw": 350.0,
                "memory_used": 8192,
                "memory_total": 24564,
                "gpu_utilization": 85.5,
                "fan_speed": 65.0
            }
        }


class BenchmarkResult(BaseModel):
    """Benchmark results"""
    test_name: str = Field(..., description="Test name")
    gpu_index: int = Field(..., description="GPU index")
    timestamp: datetime = Field(default_factory=datetime.now)
    duration: float = Field(..., description="Test duration (seconds)")
    
    # Performance metrics
    gflops: Optional[float] = Field(None, description="GFLOPS performance")
    memory_bandwidth: Optional[float] = Field(None, description="Memory bandwidth (GB/s)")
    latency: Optional[float] = Field(None, description="Latency (ms)")
    
    # Results
    success: bool = Field(..., description="Test successful?")
    error_message: Optional[str] = Field(None, description="Error message")
    
    # Additional info
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional test info")
    
    class Config:
        json_schema_extra = {
            "example": {
                "test_name": "matrix_multiply",
                "gpu_index": 0,
                "duration": 5.2,
                "gflops": 42.5,
                "memory_bandwidth": 850.3,
                "success": True
            }
        }


class HealthReport(BaseModel):
    """GPU health report"""
    gpu_index: int = Field(..., description="GPU index")
    timestamp: datetime = Field(default_factory=datetime.now)
    overall_status: HealthStatus = Field(..., description="Overall health status")
    
    # Health checks
    temperature_status: HealthStatus = Field(..., description="Temperature status")
    memory_status: HealthStatus = Field(..., description="Memory status")
    power_status: HealthStatus = Field(..., description="Power status")
    utilization_status: HealthStatus = Field(..., description="Utilization status")
    
    # Warnings and recommendations
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    
    # Latest metrics
    current_metrics: Optional[GPUMetrics] = Field(None, description="Current metrics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "gpu_index": 0,
                "overall_status": "healthy",
                "temperature_status": "healthy",
                "memory_status": "warning",
                "warnings": ["Memory usage above 90%"],
                "recommendations": ["Consider optimizing memory usage"]
            }
        }
