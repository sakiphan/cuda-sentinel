"""
Health check CLI command
"""

import click
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

@click.command()
@click.option('--detailed', '-d', is_flag=True, help='Show detailed health information')
@click.option('--json', is_flag=True, help='Output in JSON format')
@click.pass_context
def health_command(ctx, detailed: bool, json: bool):
    """Perform GPU health check"""
    from ..core.collector import GPUCollector
    
    try:
        collector = GPUCollector()
        
        if json:
            # JSON output
            import json as json_lib
            results = []
            for i in range(collector.device_count):
                health_report = collector.analyze_health(i)
                results.append(health_report.dict())
            console.print(json_lib.dumps(results, indent=2, default=str))
            return
        
        # Rich terminal output
        console.print(f"\n[bold blue]🏥 GPU Health Check[/bold blue]")
        console.print(f"[dim]Scanned GPUs: {collector.device_count}[/dim]\n")
        
        healthy_count = 0
        
        for i in range(collector.device_count):
            gpu_info = collector.get_gpu_info(i)
            health_report = collector.analyze_health(i)
            metrics = health_report.current_metrics
            
            # Status colors
            status_colors = {
                'healthy': 'green',
                'warning': 'yellow',
                'critical': 'red',
                'unknown': 'dim'
            }
            
            status_color = status_colors.get(health_report.overall_status.value, 'dim')
            status_display = f"[{status_color}]{health_report.overall_status.value.upper()}[/]"
            
            console.print(f"[bold cyan]{gpu_info.name}[/bold cyan] [dim](GPU {i})[/dim]")
            console.print(f"Status: {status_display}")
            
            if health_report.overall_status == "healthy":
                healthy_count += 1
            
            # Basic metrics table
            table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
            table.add_column("Metric", style="cyan", no_wrap=True)
            table.add_column("Value", justify="right") 
            table.add_column("Status", justify="center")
            
            # Temperature
            if metrics and metrics.temperature_gpu is not None:
                temp_status = "healthy" if metrics.temperature_gpu < 70 else "warning" if metrics.temperature_gpu < 85 else "critical"
                table.add_row("Temperature", f"{metrics.temperature_gpu:.1f}°C", temp_status)
            
            # Memory
            if metrics and metrics.memory_used and metrics.memory_total:
                memory_percent = (metrics.memory_used / metrics.memory_total) * 100
                memory_status = "healthy" if memory_percent < 80 else "warning"
                table.add_row(
                    "Memory Usage",
                    f"{memory_percent:.1f}% ({metrics.memory_used}MB / {metrics.memory_total}MB)",
                    memory_status
                )
            
            # GPU Utilization
            if metrics and metrics.gpu_utilization is not None:
                table.add_row("GPU Usage", f"{metrics.gpu_utilization:.1f}%", "📊")
            else:
                table.add_row("GPU Usage", "N/A", "📊")
            
            # Power
            if metrics and metrics.power_draw is not None:
                power_info = f"{metrics.power_draw:.3f}W"
                if metrics.power_limit:
                    power_percent = (metrics.power_draw / metrics.power_limit) * 100
                    power_info += f" ({power_percent:.1f}%)"
                table.add_row("Power Consumption", power_info, "⚡")
            
            console.print(table)
            
            # Detailed information
            if detailed:
                console.print(f"\n[bold blue]Detailed Information[/bold blue]")
                detail_table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
                detail_table.add_column("Detail", style="cyan")
                detail_table.add_column("Value", justify="right")
                
                if metrics and metrics.fan_speed is not None:
                    detail_table.add_row("Fan Speed", f"{metrics.fan_speed}%")
                else:
                    detail_table.add_row("Fan Speed", "N/A")
                
                if metrics and metrics.clock_graphics:
                    detail_table.add_row("Graphics Clock", f"{metrics.clock_graphics} MHz")
                if metrics and metrics.clock_memory:
                    detail_table.add_row("Memory Clock", f"{metrics.clock_memory} MHz")
                
                detail_table.add_row("Driver Version", gpu_info.driver_version)
                detail_table.add_row("CUDA Version", gpu_info.cuda_version)
                detail_table.add_row("Compute Capability", gpu_info.compute_capability)
                
                if metrics and metrics.ecc_errors_corrected is not None:
                    detail_table.add_row("ECC Errors (Corrected)", str(metrics.ecc_errors_corrected))
                if metrics and metrics.ecc_errors_uncorrected is not None:
                    detail_table.add_row("ECC Errors (Uncorrected)", str(metrics.ecc_errors_uncorrected))
                
                console.print(detail_table)
            
            # Warnings
            if health_report.warnings:
                console.print(f"\n[yellow]⚠️ Warnings:[/yellow]")
                for warning in health_report.warnings:
                    console.print(f"  • {warning}")
            
            # Recommendations  
            if health_report.recommendations:
                console.print(f"\n[blue]💡 Recommendations:[/blue]")
                for rec in health_report.recommendations:
                    console.print(f"  • {rec}")
            
            console.print("\n" + "─" * 60 + "\n")
        
        # Summary
        console.print(f"[bold blue]🏥 Overall Health Summary[/bold blue]")
        console.print(f"✅ Healthy: {healthy_count}")
        if healthy_count == collector.device_count:
            console.print("\n✅ All GPUs look healthy!")
        else:
            console.print(f"\n⚠️ {collector.device_count - healthy_count} GPU(s) need attention")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
