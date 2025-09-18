"""
HTTP Server for Prometheus metrics export

This module provides an HTTP server that exposes GPU metrics
in Prometheus format for monitoring and alerting.
"""

import click
import logging
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

from ..core.collector import GPUCollector
from ..exporters.prometheus import PrometheusExporter

logger = logging.getLogger(__name__)


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for serving Prometheus metrics"""
    
    def __init__(self, exporter: PrometheusExporter, *args, **kwargs):
        self.exporter = exporter
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/metrics':
            self.serve_metrics()
        elif self.path == '/health':
            self.serve_health()
        elif self.path == '/':
            self.serve_info()
        else:
            self.send_error(404, "Not Found")
    
    def serve_metrics(self):
        """Serve Prometheus metrics"""
        try:
            metrics_data = self.exporter.get_metrics()
            content_type = self.exporter.get_content_type()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(metrics_data)))
            self.end_headers()
            self.wfile.write(metrics_data)
            
        except Exception as e:
            logger.error(f"Error serving metrics: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def serve_health(self):
        """Serve health check endpoint"""
        try:
            health_data = b'{"status": "healthy", "timestamp": "' + str(time.time()).encode() + b'"}'
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(health_data)))
            self.end_headers()
            self.wfile.write(health_data)
            
        except Exception as e:
            logger.error(f"Error serving health: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def serve_info(self):
        """Serve info page"""
        info_html = """
        <html>
        <head><title>CUDA Sentinel Metrics</title></head>
        <body>
        <h1>CUDA Sentinel - GPU Monitoring</h1>
        <p>Available endpoints:</p>
        <ul>
        <li><a href="/metrics">/metrics</a> - Prometheus metrics</li>
        <li><a href="/health">/health</a> - Health check</li>
        </ul>
        </body>
        </html>
        """.encode('utf-8')
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(info_html)))
        self.end_headers()
        self.wfile.write(info_html)
    
    def log_message(self, format, *args):
        """Override to use Python logging"""
        logger.info(f"{self.address_string()} - {format % args}")


def create_handler(exporter):
    """Create a handler class with the exporter bound"""
    def handler(*args, **kwargs):
        MetricsHandler(exporter, *args, **kwargs)
    return handler


@click.command()
@click.option('--host', '-h', default='0.0.0.0', help='Host to bind to')
@click.option('--port', '-p', default=8080, help='Port to bind to')
@click.option('--interval', '-i', default=10, help='Metrics collection interval (seconds)')
def server_command(host: str, port: int, interval: int):
    """Start HTTP server for Prometheus metrics export"""
    
    try:
        # Initialize collector and exporter
        collector = GPUCollector()
        exporter = PrometheusExporter(collector)
        
        # Create HTTP server
        server_address = (host, port)
        handler_class = lambda *args, **kwargs: MetricsHandler(exporter, *args, **kwargs)
        httpd = HTTPServer(server_address, handler_class)
        
        print(f"🚀 CUDA Sentinel server starting on {host}:{port}")
        print(f"📊 Metrics endpoint: http://{host}:{port}/metrics")
        print(f"🏥 Health endpoint: http://{host}:{port}/health")
        print(f"🔄 Collection interval: {interval}s")
        print("Press Ctrl+C to stop")
        
        # Start background metrics collection
        def collect_metrics():
            while True:
                try:
                    exporter.collect()
                    time.sleep(interval)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Error in background collection: {e}")
                    time.sleep(interval)
        
        collector_thread = Thread(target=collect_metrics, daemon=True)
        collector_thread.start()
        
        # Start HTTP server
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        logger.error(f"Server error: {e}", exc_info=True)
