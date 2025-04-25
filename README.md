# Leneda Fetch

A collection of Python scripts for querying and analyzing Leneda energy data. These scripts provide a command-line interface to fetch, process, and display energy consumption data from Leneda's API.

## Features

- Interactive POD (Point of Delivery) selection
- Monthly data retrieval
- Data processing and analysis
- Raw JSON data download
- ASCII art display of user information

## Prerequisites

- Python 3.6 or higher
- Required Python packages (install via pip):
  ```bash
  pip install requests pyyaml python-dateutil pyfiglet
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/leneda-fetch.git
   cd leneda-fetch
   ```

2. Create a `config.yaml` file in the project directory with your Leneda API configuration:
   ```yaml
   url: "https://api.leneda.com/v1/pods/%s/measurements"
   headers:
     Authorization: "Bearer your-api-token"
   PODs:
     - name: "Home"
       id: "your-pod-id"
       threshold: 7
     - name: "Office"
       id: "another-pod-id"
       threshold: 12
   threshold_price:
     7: 10.0
     12: 15.0
   ```

## Usage

### Fetch and Process Data

The `fetch.py` script retrieves and processes energy consumption data:

```bash
python fetch.py
```

This will:
1. Display a list of configured PODs for selection
2. Show available months for data retrieval
3. Process and display the data with:
   - Daily consumption statistics
   - Threshold exceedances
   - Cost calculations
   - Monthly estimates (if applicable)

### Download Raw Data

The `download.py` script downloads raw JSON data from the API:

```bash
python download.py
```

This will:
1. Display a list of configured PODs for selection
2. Show available months for data retrieval
3. Save the raw JSON response to a file named `YYYY-MM-timestamp.json`

## Configuration

The `config.yaml` file contains all necessary configuration:

- `url`: API endpoint URL with `%s` placeholder for POD ID
- `headers`: API authentication headers
- `PODs`: List of configured PODs with:
  - `name`: Display name
  - `id`: POD identifier
  - `threshold`: Energy threshold in kWh
- `threshold_price`: Price mapping for different thresholds

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
