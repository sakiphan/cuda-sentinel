"""
Export CLI command - Export metrics in various formats
"""

import click
from rich.console import Console

console = Console()

@click.command()
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'prometheus']), 
              default='json', help='Export format')
@click.option('--output', '-o', help='Output file (default: stdout)')
@click.option('--gpu', '-g', type=int, help='Export specific GPU (default: all)')
@click.option('--metrics-only', is_flag=True, help='Export only metrics (exclude health data)')
def export_command(format: str, output: str, gpu: int, metrics_only: bool):
    """Export GPU metrics and health data"""
    from ..core.collector import GPUCollector
    import json
    import csv
    import io
    
    try:
        collector = GPUCollector()
        
        if gpu is not None and gpu >= collector.device_count:
            console.print(f"[red]Error: GPU {gpu} not found. Available GPUs: 0-{collector.device_count-1}[/red]")
            return
        
        gpus_to_export = [gpu] if gpu is not None else list(range(collector.device_count))
        
        # Collect data
        data = []
        for gpu_idx in gpus_to_export:
            gpu_info = collector.get_gpu_info(gpu_idx)
            metrics = collector.collect_metrics(gpu_idx)
            
            if metrics_only:
                item = {
                    'gpu_index': gpu_idx,
                    'gpu_name': gpu_info.name,
                    **metrics.dict()
                }
            else:
                health_report = collector.analyze_health(gpu_idx)
                item = {
                    'gpu_info': gpu_info.dict(),
                    'metrics': metrics.dict(),
                    'health': health_report.dict()
                }
            
            data.append(item)
        
        # Format output
        if format == 'json':
            output_str = json.dumps(data, indent=2, default=str)
        
        elif format == 'csv':
            output_buffer = io.StringIO()
            
            if data:
                if metrics_only:
                    # Flatten metrics for CSV
                    fieldnames = set()
                    for item in data:
                        fieldnames.update(item.keys())
                    fieldnames = sorted(fieldnames)
                    
                    writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
                    writer.writeheader()
                    for item in data:
                        # Convert complex types to strings
                        csv_item = {}
                        for k, v in item.items():
                            csv_item[k] = str(v) if v is not None else ''
                        writer.writerow(csv_item)
                else:
                    # For full data, create separate sections
                    writer = csv.writer(output_buffer)
                    writer.writerow(['GPU_Index', 'Section', 'Field', 'Value'])
                    
                    for item in data:
                        gpu_idx = item['gpu_info']['index']
                        
                        # GPU Info
                        for k, v in item['gpu_info'].items():
                            writer.writerow([gpu_idx, 'gpu_info', k, str(v)])
                        
                        # Metrics
                        for k, v in item['metrics'].items():
                            if v is not None:
                                writer.writerow([gpu_idx, 'metrics', k, str(v)])
                        
                        # Health
                        for k, v in item['health'].items():
                            if k not in ['current_metrics']:  # Skip nested metrics
                                writer.writerow([gpu_idx, 'health', k, str(v)])
            
            output_str = output_buffer.getvalue()
        
        elif format == 'prometheus':
            # Basic Prometheus format
            lines = []
            lines.append('# HELP gpu_temperature_celsius GPU temperature in Celsius')
            lines.append('# TYPE gpu_temperature_celsius gauge')
            
            for item in data:
                if metrics_only:
                    gpu_idx = item['gpu_index']
                    gpu_name = item['gpu_name']
                    
                    if item.get('temperature_gpu'):
                        lines.append(f'gpu_temperature_celsius{{gpu="{gpu_idx}",name="{gpu_name}"}} {item["temperature_gpu"]}')
                    
                    if item.get('memory_used') and item.get('memory_total'):
                        memory_percent = (item['memory_used'] / item['memory_total']) * 100
                        lines.append(f'gpu_memory_usage_percent{{gpu="{gpu_idx}",name="{gpu_name}"}} {memory_percent:.2f}')
                    
                    if item.get('gpu_utilization'):
                        lines.append(f'gpu_utilization_percent{{gpu="{gpu_idx}",name="{gpu_name}"}} {item["gpu_utilization"]}')
                    
                    if item.get('power_draw'):
                        lines.append(f'gpu_power_draw_watts{{gpu="{gpu_idx}",name="{gpu_name}"}} {item["power_draw"]}')
                
                else:
                    gpu_info = item['gpu_info']
                    metrics = item['metrics']
                    
                    gpu_idx = gpu_info['index']
                    gpu_name = gpu_info['name']
                    
                    if metrics.get('temperature_gpu'):
                        lines.append(f'gpu_temperature_celsius{{gpu="{gpu_idx}",name="{gpu_name}"}} {metrics["temperature_gpu"]}')
                    
                    if metrics.get('memory_used') and metrics.get('memory_total'):
                        memory_percent = (metrics['memory_used'] / metrics['memory_total']) * 100
                        lines.append(f'gpu_memory_usage_percent{{gpu="{gpu_idx}",name="{gpu_name}"}} {memory_percent:.2f}')
                    
                    if metrics.get('gpu_utilization'):
                        lines.append(f'gpu_utilization_percent{{gpu="{gpu_idx}",name="{gpu_name}"}} {metrics["gpu_utilization"]}')
                    
                    if metrics.get('power_draw'):
                        lines.append(f'gpu_power_draw_watts{{gpu="{gpu_idx}",name="{gpu_name}"}} {metrics["power_draw"]}')
            
            output_str = '\n'.join(lines) + '\n'
        
        # Output
        if output:
            with open(output, 'w') as f:
                f.write(output_str)
            console.print(f"[green]✅ Data exported to {output}[/green]")
        else:
            console.print(output_str)
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
