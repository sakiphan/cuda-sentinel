"""
Benchmark Runner - Manages execution of GPU benchmark tests

This module provides the BenchmarkRunner class that orchestrates
the execution of various benchmark tests.
"""

import logging
from typing import List, Dict, Type, Optional

from .base import BaseBenchmark
from .tests import MatrixMultiplicationBenchmark, MemoryBandwidthBenchmark, SimpleBenchmark
from ..core.models import BenchmarkResult

logger = logging.getLogger(__name__)


class BenchmarkRunner:
    """Manages and executes GPU benchmark tests"""
    
    def __init__(self):
        self.available_benchmarks: Dict[str, Type[BaseBenchmark]] = {
            "matrix_multiply": MatrixMultiplicationBenchmark,
            "memory_bandwidth": MemoryBandwidthBenchmark,
            "simple": SimpleBenchmark
        }
    
    def list_available_benchmarks(self) -> List[str]:
        """Get list of available benchmark names"""
        return list(self.available_benchmarks.keys())
    
    def run_benchmark(self, benchmark_name: str, gpu_index: int, **kwargs) -> BenchmarkResult:
        """Run a specific benchmark test"""
        if benchmark_name not in self.available_benchmarks:
            raise ValueError(f"Unknown benchmark: {benchmark_name}. Available: {self.list_available_benchmarks()}")
        
        benchmark_class = self.available_benchmarks[benchmark_name]
        benchmark = benchmark_class(gpu_index, **kwargs)
        
        logger.info(f"Running benchmark '{benchmark_name}' on GPU {gpu_index}")
        result = benchmark.execute()
        
        if result.success:
            logger.info(f"Benchmark '{benchmark_name}' completed successfully: {result.gflops:.2f} GFLOPS")
        else:
            logger.warning(f"Benchmark '{benchmark_name}' failed: {result.error_message}")
        
        return result
    
    def run_all_benchmarks(self, gpu_index: int, **kwargs) -> List[BenchmarkResult]:
        """Run all available benchmarks on a GPU"""
        results = []
        
        for benchmark_name in self.available_benchmarks:
            try:
                result = self.run_benchmark(benchmark_name, gpu_index, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to run benchmark '{benchmark_name}': {e}")
                # Create a failed result
                failed_result = BenchmarkResult(
                    test_name=benchmark_name,
                    gpu_index=gpu_index,
                    duration=0.0,
                    success=False,
                    error_message=str(e)
                )
                results.append(failed_result)
        
        return results
    
    def run_specific_benchmarks(self, benchmark_names: List[str], gpu_index: int, **kwargs) -> List[BenchmarkResult]:
        """Run specific benchmarks on a GPU"""
        results = []
        
        for benchmark_name in benchmark_names:
            try:
                result = self.run_benchmark(benchmark_name, gpu_index, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to run benchmark '{benchmark_name}': {e}")
                failed_result = BenchmarkResult(
                    test_name=benchmark_name,
                    gpu_index=gpu_index,
                    duration=0.0,
                    success=False,
                    error_message=str(e)
                )
                results.append(failed_result)
        
        return results
    
    def get_benchmark_info(self, benchmark_name: str) -> Optional[Dict[str, str]]:
        """Get information about a specific benchmark"""
        if benchmark_name not in self.available_benchmarks:
            return None
        
        benchmark_class = self.available_benchmarks[benchmark_name]
        return {
            "name": benchmark_name,
            "class": benchmark_class.__name__,
            "description": benchmark_class.__doc__ or "No description available"
        }
