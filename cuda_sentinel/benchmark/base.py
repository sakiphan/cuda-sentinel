"""
Base benchmark class - Foundation for all benchmark tests

This module provides the base benchmark class that all specific
benchmark implementations should inherit from.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ..core.models import BenchmarkResult

logger = logging.getLogger(__name__)


class BaseBenchmark(ABC):
    """Base class for all GPU benchmark tests"""
    
    def __init__(self, gpu_index: int, test_name: str):
        self.gpu_index = gpu_index
        self.test_name = test_name
        self.metadata = {}
    
    @abstractmethod
    def setup(self) -> bool:
        """Setup the benchmark test. Return True if successful."""
        pass
    
    @abstractmethod
    def run_test(self) -> Dict[str, Any]:
        """Run the actual benchmark test. Return results dictionary."""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Cleanup after the benchmark test."""
        pass
    
    def execute(self) -> BenchmarkResult:
        """Execute the complete benchmark workflow"""
        start_time = time.time()
        success = False
        error_message = None
        results = {}
        
        try:
            # Setup phase
            if not self.setup():
                raise RuntimeError("Benchmark setup failed")
            
            # Run test
            results = self.run_test()
            success = True
            
        except Exception as e:
            logger.error(f"Benchmark {self.test_name} failed: {e}")
            error_message = str(e)
            
        finally:
            # Always cleanup
            try:
                self.cleanup()
            except Exception as e:
                logger.warning(f"Cleanup failed for {self.test_name}: {e}")
        
        duration = time.time() - start_time
        
        return BenchmarkResult(
            test_name=self.test_name,
            gpu_index=self.gpu_index,
            duration=duration,
            gflops=results.get('gflops'),
            memory_bandwidth=results.get('memory_bandwidth_gbps'),
            latency=results.get('latency_ms'),
            success=success,
            error_message=error_message,
            metadata={**self.metadata, **results}
        )
