"""
Exception classes for CUDA Sentinel

Custom exceptions for GPU monitoring and NVML operations.
"""


class CudaSentinelError(Exception):
    """Base exception for CUDA Sentinel operations"""
    pass


class NVMLError(CudaSentinelError):
    """Exception raised when NVML operations fail"""
    
    def __init__(self, message: str, nvml_error_code: int = None):
        super().__init__(message)
        self.nvml_error_code = nvml_error_code
        
    def __str__(self):
        if self.nvml_error_code:
            return f"NVML Error {self.nvml_error_code}: {super().__str__()}"
        return super().__str__()


class GPUNotFoundError(CudaSentinelError):
    """Exception raised when specified GPU is not found"""
    
    def __init__(self, gpu_index: int):
        self.gpu_index = gpu_index
        super().__init__(f"GPU {gpu_index} not found")


class BenchmarkError(CudaSentinelError):
    """Exception raised when benchmark operations fail"""
    pass
