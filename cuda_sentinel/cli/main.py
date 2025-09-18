"""
Main CLI entry point for CUDA Sentinel

Provides the main command-line interface using Click framework.
"""

import click
from rich.console import Console

console = Console()

@click.group()
@click.version_option(version="0.1.0")
@click.pass_context
def cli(ctx):
    """🚀 CUDA Sentinel - GPU Health Monitoring Tool
    
    A comprehensive toolkit for monitoring NVIDIA GPU health,
    performance, and running diagnostics.
    """
    ctx.ensure_object(dict)
    
    # Show banner on help
    if ctx.get_parameter_source('help') == click.core.ParameterSource.COMMANDLINE:
        console.print("""
[bold blue]🚀 CUDA Sentinel[/bold blue] [dim]v0.1.0[/dim]
[cyan]GPU Health Monitoring & Benchmarking Tool[/cyan]

Monitor your NVIDIA GPUs with real-time metrics,
health analysis, and performance benchmarks.
        """)

# Import and register commands
from .health import health_command
from .monitor import monitor_command
from .benchmark import benchmark_command
from .exporter import export_command
from .server import server_command

cli.add_command(health_command, name="health")
cli.add_command(monitor_command, name="monitor") 
cli.add_command(benchmark_command, name="benchmark")
cli.add_command(export_command, name="export")
cli.add_command(server_command, name="server")

if __name__ == "__main__":
    cli()
