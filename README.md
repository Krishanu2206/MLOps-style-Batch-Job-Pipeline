# Minimal MLOps-style Batch Job Pipeline

## Deliverables

The repository includes the required files:

- `run.py`
- `config.yaml`
- `data.csv`
- `requirements.txt`
- `Dockerfile`
- `README.md`
- `metrics.json`
- `run.log`

## Local Run Instructions

1. Open a terminal in the project root.
2. Create a virtual environment:

   ```bash / cmd
   python -m venv .venv
   ```

3. Activate the environment in bash:

   ```bash
   source .venv/Scripts/activate
   ```

   OR (FOR WINDOWS)

   ```cmd
   .venv\Scripts\activate
   ```

4. Install the dependencies:

   ```bash / cmd
   pip install -r requirements.txt
   ```

5. Run the pipeline:

   ```bash / cmd
   python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
   ```

6. After the run completes, check `metrics.json` for the JSON output and `run.log` for the execution log.

Note: The pinned dependencies in `requirements.txt` are intended for Python 3.9, which matches the Docker image. If your default `python` points to a newer interpreter, create the virtual environment with Python 3.9 before activating it.

## Docker Build and Run Commands

1. Build the image:

   ```bash / cmd
   docker build -t mlops-task .
   ```

2. Run the container:

   ```bash / cmd
   docker run --rm mlops-task
   ```

The container uses the default command defined in the Dockerfile:

```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

## Example metrics.json

Successful runs produce a metrics file like this:

```json
{
  "version": "v1",
  "rows_processed": 9996,
  "metric": "signal_rate",
  "value": 0.4991,
  "latency_ms": 31,
  "seed": 42,
  "status": "success"
}
```

## Example run.log

Successful runs produce logs similar to the following:

```text
2026-05-20 20:48:18,750 [INFO] Job initiated. Starting validation and processing lifecycle.
2026-05-20 20:48:18,751 [INFO] Loading configuration from path: config.yaml
2026-05-20 20:48:18,752 [INFO] Config successfully validated. Version: v1 | Seed: 42 | Window: 5
2026-05-20 20:48:18,753 [INFO] Reading dataset from path: data.csv
2026-05-20 20:48:18,773 [INFO] Dataset successfully validated and loaded. Total rows: 10000
2026-05-20 20:48:18,775 [INFO] Computing rolling average on Close metric.
2026-05-20 20:48:18,777 [INFO] Generating vectorized binary signals.
2026-05-20 20:48:18,782 [INFO] Execution complete. Performance Metrics written to metrics.json
2026-05-20 20:48:18,782 [INFO] Metrics Summary -> Rows Processed: 9996 | Signal Rate: 0.4991 | Latency: 31ms
2026-05-20 20:48:18,783 [INFO] Job ended. Status: success
2026-05-20 20:48:18,783 [INFO] Exit code: 0 (success)
```
