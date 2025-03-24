# BacktestEngine & TradingEngine

This project contains two simulation engines for testing trading strategies: **BacktestEngine** and **TradingEngine**. Both engines use historical data to simulate trades, with BacktestEngine focused on backtesting and TradingEngine potentially for extended testing.

## Docker & Script Usage

To simplify setup and ensure a consistent environment, we provide a Dockerfile and related scripts.

1. **Building the Docker Image:**
   - Ensure you have Docker installed.
   - Use the provided build script to create the Docker image.
     ```
     bash ./bash/build.sh
     ```
   - This script checks for an existing `.env` (or creates one from `.env.example`), builds the Docker image based on `Dockerfile`, and runs the container.

2. **Installing TA-Lib:**
   - The Dockerfile copies and executes the `install_talib.sh` script, which downloads, builds, and installs TA-Lib, then installs its Python package.

3. **Running the Container:**
   - The build script also starts a container mounting the current directory to `/app`. Inside the container, you can run the Python scripts (e.g., `BacktestEngine.py` or `TradingEngine.py`).

## Project Overview

### BacktestEngine
- **Purpose:** Simulate trading strategies using historical data.
- **Features:**
  - Open/close long and short positions.
  - Calculate position size with configurable capital, fee rate, and leverage.
  - Log trade details and analyze results.
- **Usage:**
  ```bash
  python /app/BacktestEngine.py
  ```

### TradingEngine
- **Purpose:** Similar to BacktestEngine with potential modifications for live or extended simulation.
- **Features:** Same as BacktestEngine.
- **Usage:**
  ```bash
  python /app/TradingEngine.py
  ```