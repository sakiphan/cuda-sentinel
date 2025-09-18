"""
Benchmark CLI command
"""

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@click.command()
@click.option('--gpu', '-g', type=int, help='GPU to benchmark (default: all)')
@click.option('--test', '-t', default='simple', help='Benchmark test to run')
@click.option('--iterations', '-n', default=1, help='Number of iterations')
def benchmark_command(gpu: int, test: str, iterations: int):
    """Run GPU benchmark tests"""
    from ..core.collector import GPUCollector
    
    try:
        collector = GPUCollector()
        
        if gpu is not None and gpu >= collector.device_count:
            console.print(f"[red]Error: GPU {gpu} not found. Available GPUs: 0-{collector.device_count-1}[/red]")
            return
        
        gpus_to_test = [gpu] if gpu is not None else list(range(collector.device_count))
        
        console.print(f"[bold blue]🏃‍♂️ Running benchmark tests...[/bold blue]")
        console.print(f"[dim]Test: {test} | Iterations: {iterations} | GPUs: {', '.join(map(str, gpus_to_test))}[/dim]\n")
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for gpu_idx in gpus_to_test:
                gpu_info = collector.get_gpu_info(gpu_idx)
                task = progress.add_task(f"Benchmarking GPU {gpu_idx} ({gpu_info.name})...", total=None)
                
                gpu_results = []
                for i in range(iterations):
                    if iterations > 1:
                        progress.update(task, description=f"GPU {gpu_idx} - Iteration {i+1}/{iterations}")
                    
                    result = collector.run_simple_benchmark(gpu_idx)
                    gpu_results.append(result)
                
                results.extend(gpu_results)
                progress.update(task, completed=True)
        
        # Display results
        console.print("\n[bold blue]📊 Benchmark Results[/bold blue]\n")
        
        for gpu_idx in gpus_to_test:
            gpu_info = collector.get_gpu_info(gpu_idx)
            gpu_results = [r for r in results if r.gpu_index == gpu_idx]
            
            console.print(f"[bold cyan]{gpu_info.name}[/bold cyan] [dim](GPU {gpu_idx})[/dim]")
            
            if not gpu_results:
                console.print("[red]No results[/red]\n")
                continue
            
            successful_results = [r for r in gpu_results if r.success]
            
            if not successful_results:
                console.print("[red]All tests failed[/red]")
                for result in gpu_results:
                    if result.error_message:
                        console.print(f"  Error: {result.error_message}")
                console.print()
                continue
            
            # Calculate averages
            avg_duration = sum(r.duration for r in successful_results) / len(successful_results)
            avg_gflops = sum(r.gflops for r in successful_results if r.gflops) / len([r for r in successful_results if r.gflops])
            
            console.print(f"  ✅ Success Rate: {len(successful_results)}/{len(gpu_results)}")
            console.print(f"  ⏱️ Average Duration: {avg_duration:.3f}s")
            if avg_gflops:
                console.print(f"  🚀 Average Performance: {avg_gflops:.2f} GFLOPS")
            
            if iterations > 1:
                console.print(f"  📈 Best Performance: {max(r.gflops for r in successful_results if r.gflops):.2f} GFLOPS")
                console.print(f"  📉 Worst Performance: {min(r.gflops for r in successful_results if r.gflops):.2f} GFLOPS")
            
            console.print()
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
