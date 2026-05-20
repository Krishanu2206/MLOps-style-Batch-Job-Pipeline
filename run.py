import argparse
import json
import logging
import os
import sys
import time
import numpy as np
import pandas as pd
import yaml

def setup_logging(log_file_path):
    """Configures logging to write to both a file and standard output."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler(sys.stdout)
        ]
    )

def write_metrics(path, data):
    """Safely writes the metrics dictionary to the designated JSON path."""
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Critical Error: Could not write metrics file to {path}. Details: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Deterministic MLOps Batch Processing Pipeline")
    parser.add_argument("--input", required=True, help="Path to input data.csv")
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    parser.add_argument("--output", required=True, help="Path to output metrics.json")
    parser.add_argument("--log-file", required=True, help="Path to output run.log")
    args = parser.parse_args()

    start_time = time.time()
    config_version = "unknown"
    provided_seed = None
    exit_code = 1
    job_status = "failure"

    setup_logging(args.log_file)
    logging.info("Job initiated. Starting validation and processing lifecycle.")

    try:
        logging.info(f"Loading configuration from path: {args.config}")
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Configuration file not found at path: {args.config}")
        
        with open(args.config, 'r') as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as ye:
                raise ValueError(f"Invalid YAML structure or formatting error: {ye}")

        if not config:
            raise ValueError("Configuration file is empty.")

        required_fields = ['seed', 'window', 'version']
        for field in required_fields:
            if field not in config:
                raise KeyError(f"Missing mandatory configuration field: '{field}'")

        config_version = str(config['version'])
        provided_seed = int(config['seed'])
        window = int(config['window'])

        if window <= 0:
            raise ValueError(f"Rolling window parameter must be a positive integer. Provided: {window}")

        np.random.seed(provided_seed)
        logging.info(f"Config successfully validated. Version: {config_version} | Seed: {provided_seed} | Window: {window}")

        logging.info(f"Reading dataset from path: {args.input}")
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input data file not found at path: {args.input}")
        
        if os.path.getsize(args.input) == 0:
            raise ValueError("Input data file is completely empty.")

        try:
            df = pd.read_csv(args.input)
        except Exception as ce:
            raise ValueError(f"Invalid CSV format or parsing structural error: {ce}")

        if df.empty:
            raise ValueError("Parsed CSV dataset contains zero data rows.")

        if 'close' not in df.columns:
            raise ValueError("Missing required column 'close' inside input dataset.")

        rows_loaded = len(df)
        logging.info(f"Dataset successfully validated and loaded. Total rows: {rows_loaded}")

        logging.info("Computing rolling average on Close metric.")

        df['rolling_mean'] = df['close'].rolling(window=window).mean()

        logging.info("Generating vectorized binary signals.")

        df['signal'] = np.where(df['close'] > df['rolling_mean'], 1, 0)
        
        valid_rows = df.dropna(subset=['rolling_mean'])
        
        if valid_rows.empty:
            raise ValueError(f"Dataset length ({rows_loaded}) is smaller than or equal to the configuration window size ({window}).")

        processed_count = len(valid_rows)
        signal_rate = float(valid_rows['signal'].mean())
        
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        success_metrics = {
            "version": config_version,
            "rows_processed": processed_count,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": provided_seed,
            "status": "success"
        }

        write_metrics(args.output, success_metrics)
        logging.info(f"Execution complete. Performance Metrics written to {args.output}")
        logging.info(f"Metrics Summary -> Rows Processed: {processed_count} | Signal Rate: {success_metrics['value']} | Latency: {latency_ms}ms")
        
        print(json.dumps(success_metrics, indent=2))
        exit_code = 0
        job_status = "success"

    except Exception as error:
        error_message = str(error)
        logging.error(f"Execution pipeline encountered a fatal event: {error_message}", exc_info=True)
        
        error_metrics = {
            "version": config_version,
            "status": "error",
            "error_message": error_message
        }
        
        write_metrics(args.output, error_metrics)
        print(json.dumps(error_metrics, indent=2))
    finally:
        logging.info(f"Job ended. Status: {job_status}")
        logging.info(f"Exit code: {exit_code} ({'success' if exit_code == 0 else 'failure'})")

    sys.exit(exit_code)

if __name__ == "__main__":
    main()