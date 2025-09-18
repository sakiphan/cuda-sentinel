"""
Monitor CLI command - Continuous GPU monitoring
"""

import click
import time
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich import box

console = Console()

@click.command()
@click.option('--interval', '-i', default=5, help='Update interval in seconds')
@click.option('--gpu', '-g', type=int, help='Monitor specific GPU (default: all)')
@click.option('--duration', '-d', type=int, help='Total monitoring duration in seconds')
def monitor_command(interval: int, gpu: int, duration: int):
    """Start continuous GPU monitoring"""
    from ..core.collector import GPUCollector
    
    try:
        collector = GPUCollector()
        
        if gpu is not None and gpu >= collector.device_count:
            console.print(f"[red]Error: GPU {gpu} not found. Available GPUs: 0-{collector.device_count-1}[/red]")
            return
        
        gpus_to_monitor = [gpu] if gpu is not None else list(range(collector.device_count))
        
        console.print(f"[bold blue]🔄 Starting GPU monitoring...[/bold blue]")
        console.print(f"[dim]Update interval: {interval}s | GPUs: {', '.join(map(str, gpus_to_monitor))}[/dim]")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")
        
        start_time = time.time()
        
        def generate_table():
            table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
            table.add_column("GPU", style="cyan")
            table.add_column("Name", style="white")
            table.add_column("Temp", justify="right")
            table.add_column("Memory", justify="right")
            table.add_column("GPU%", justify="right")
            table.add_column("Power", justify="right")
            table.add_column("Status")
            
            for gpu_idx in gpus_to_monitor:
                try:
                    gpu_info = collector.get_gpu_info(gpu_idx)
                    metrics = collector.collect_metrics(gpu_idx)
                    health = collector.analyze_health(gpu_idx)
                    
                    # Status color
                    status_colors = {
                        'healthy': '[green]●[/green]',
                        'warning': '[yellow]●[/yellow]',
                        'critical': '[red]●[/red]',
                        'unknown': '[dim]●[/dim]'
                    }
                    status_icon = status_colors.get(health.overall_status.value, '[dim]●[/dim]')
                    
                    # Temperature
                    temp_str = f"{metrics.temperature_gpu:.1f}°C" if metrics.temperature_gpu else "N/A"
                    
                    # Memory
                    if metrics.memory_used and metrics.memory_total:
                        memory_percent = (metrics.memory_used / metrics.memory_total) * 100
                        memory_str = f"{memory_percent:.1f}%"
                    else:
                        memory_str = "N/A"
                    
                    # GPU utilization
                    gpu_util_str = f"{metrics.gpu_utilization:.1f}%" if metrics.gpu_utilization else "N/A"
                    
                    # Power
                    power_str = f"{metrics.power_draw:.1f}W" if metrics.power_draw else "N/A"
                    
                    # Truncate GPU name for display
                    gpu_name = gpu_info.name
                    if len(gpu_name) > 20:
                        gpu_name = gpu_name[:17] + "..."
                    
                    table.add_row(
                        str(gpu_idx),
                        gpu_name,
                        temp_str,
                        memory_str,
                        gpu_util_str, 
                        power_str,
                        status_icon
                    )
                    
                except Exception as e:
                    table.add_row(
                        str(gpu_idx),
                        "Error",
                        "N/A",
                        "N/A", 
                        "N/A",
                        "N/A",
                        "[red]✗[/red]"
                    )
            
            return table
        
        with Live(generate_table(), refresh_per_second=1) as live:
            try:
                while True:
                    # Check duration limit
                    if duration and (time.time() - start_time) >= duration:
                        break
                    
                    live.update(generate_table())
                    time.sleep(interval)
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Monitoring stopped by user[/yellow]")
        
        console.print("[green]✅ Monitoring completed[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
