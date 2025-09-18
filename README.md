# CUDA Sentinel

**GPU Health & Performance Monitoring System**

A real-time monitoring and benchmarking tool for CUDA GPUs. Provides comprehensive GPU observability with Prometheus metrics and Grafana dashboards.

## 🎯 Features

* 📊 **GPU Metrics**: Temperature, power, memory usage, clock speeds
* 🚨 **Throttling Detection**: Thermal and power throttling states
* 📈 **Prometheus Integration**: 60+ metrics automatically exported
* 🖥️ **Grafana Dashboard**: Ultimate GPU Dashboard with 19 visualization panels
* 🧪 **Benchmark Tests**: GFLOPS and memory bandwidth measurement
* ⚠️ **ECC Error Monitoring**: Memory error tracking
* 🔧 **CLI Tools**: Easy-to-use command line interface

## 🛠️ Requirements

* **GPU**: NVIDIA GPU (CUDA 11.0+)
* **OS**: Linux (tested on Ubuntu 20.04+)
* **Python**: 3.8+
* **NVIDIA Drivers**: 450.80.02+
* **Docker**: 20.10+ (optional)

**Tested on**: NVIDIA L40S GPUs

## 🚀 Installation & Usage

### Method 1: Docker Compose (Recommended)

```bash
# Clone the project
git clone https://github.com/username/cuda-sentinel.git
cd cuda-sentinel

# Start the monitoring stack
docker compose up -d

# Access the Ultimate GPU Dashboard
# Grafana: http://localhost:3000 (admin/admin)
# Dashboard: "CUDA Sentinel - Ultimate GPU Dashboard (60+ Metrics)"
```

### Method 2: Manual Setup

```bash
# Install Python dependencies
pip install -r requirements.txt
pip install -e .

# Run a GPU health check
cuda-sentinel health --detailed

# Start Prometheus metrics exporter
cuda-sentinel exporter --format prometheus --port 8080
```

## 📊 Collected Metrics

### Core GPU Metrics (35+)

* **Temperature**: Core + Memory temperature monitoring
* **Power**: Current draw, limits, and efficiency tracking
* **Memory**: Usage, utilization, reserved, and process allocation
* **Utilization**: Compute, encoder, decoder workload tracking
* **Clock Speeds**: Current and maximum frequencies (Graphics/Memory/SM)

### Advanced Hardware Metrics (25+)

* **PCIe Performance**: Generation (3.0/4.0/5.0), link width (x1-x16), throughput
* **Throttling Detection**: 8 detailed throttling reasons (thermal, power, etc.)
* **ECC Memory Health**: Single/double bit errors, retired pages
* **Performance States**: P-State monitoring (P0-P15)
* **Process Monitoring**: Active process count and memory usage

### Benchmark & Performance Metrics

* **GFLOPS Performance**: `cuda_sentinel_benchmark_gflops`
* **Memory Bandwidth**: `cuda_sentinel_benchmark_memory_bandwidth_gbps` (requires benchmark)
* **Collection Performance**: `cuda_sentinel_scrape_duration_seconds`

### Multi-GPU Features

* **P2P Connectivity**: Direct memory access status between GPUs
* **Topology Mapping**: Inter-GPU communication capabilities
* **Individual GPU Tracking**: All metrics tagged with GPU ID and UUID

**Total**: 60+ comprehensive metrics across all areas

## 🎛️ Usage

### CLI Commands

```bash
# Check GPU health
cuda-sentinel health

# Detailed health report
cuda-sentinel health --detailed

# Continuous monitoring (60 minutes)
cuda-sentinel monitor --duration 3600

# Run benchmarks
cuda-sentinel benchmark --type all

# Export metrics
cuda-sentinel exporter --format prometheus --port 8080
cuda-sentinel exporter --format json --output metrics.json
cuda-sentinel exporter --format csv --output metrics.csv
```

### Dashboard Access

1. **Grafana**: [http://localhost:3000](http://localhost:3000) (admin/admin)
   - **"CUDA Sentinel - Ultimate GPU Dashboard (60+ Metrics)"** - Auto-loaded!
2. **Prometheus**: [http://localhost:9090](http://localhost:9090)
3. **CUDA Sentinel API**: [http://localhost:8081/metrics](http://localhost:8081/metrics)

## 📋 Project Structure

```
cuda_sentinel/
├── core/           # GPU collector and health checks
├── exporters/      # Prometheus, JSON, CSV exporters  
├── cli/            # Command line interface
├── benchmark/      # Performance test modules
├── grafana/        # Dashboard templates
└── docker/         # Docker configurations
```

## 🔧 Configuration

### Environment Variables

```bash
# Select specific GPUs
export CUDA_VISIBLE_DEVICES=0,1

# Logging level
export CUDA_SENTINEL_LOG_LEVEL=INFO

# Metrics collection interval
export CUDA_SENTINEL_REFRESH_INTERVAL=10
```

### Grafana Dashboard

The **"CUDA Sentinel - Ultimate GPU Dashboard (60+ Metrics)"** is loaded automatically and includes **19 panels**:

**🌡️ Temperature & Power (Panels 1-2)**
* Core + Memory temperature monitoring
* Power consumption vs limits

**📊 Utilization & Memory (Panels 3-5)**  
* GPU compute, encoder, decoder utilization
* Memory usage (bytes + percentage + reserved + process)

**⚙️ Performance Monitoring (Panels 6-10)**
* Current vs Maximum clock speeds
* PCIe throughput (TX/RX)
* Health status and P-State tracking

**🚨 Advanced Diagnostics (Panels 11-17)**
* Detailed throttling reasons (6 different causes)
* Benchmark performance (GFLOPS)
* Memory bandwidth (when benchmarks run)
* Active processes and ECC memory health
* PCIe topology (Generation + Link Width)

**📈 System Overview (Panels 18-19)**
* System-wide summary (6 key metrics)
* Scrape performance and collection timing

**Optimized for**: NVIDIA L40S professional GPU monitoring

## 🧪 Tested On

* **Hardware**: 2x NVIDIA L40S GPUs
* **OS**: Ubuntu 22.04
* **Driver**: NVIDIA 535.xx
* **CUDA**: 11.8

## 🔍 Troubleshooting

```bash
# Verify GPU detection
nvidia-smi

# Check CUDA Sentinel version
cuda-sentinel --version

# Debug mode
cuda-sentinel --debug health

# Validate metrics
curl http://localhost:8081/metrics | grep cuda_sentinel

# Run benchmark to populate performance metrics
cuda-sentinel benchmark --test matrix_multiply --iterations 3
```

**Note**: This tool has been tested on NVIDIA L40S GPUs. Compatibility with other models is not guaranteed.

---