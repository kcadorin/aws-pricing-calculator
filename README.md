# AWS Cost Calculator

A Streamlit application to estimate AWS service costs and generate spending forecasts.

## Overview

This calculator allows you to select different AWS services, configure their characteristics, and obtain a monthly cost estimate. The application uses approximate pricing data based on AWS pricing tables.

## Supported Services

- EC2 (Compute Instances)
- S3 (Object Storage)
- Fargate/ECS (Containers)
- Lambda (Serverless Computing)
- ECR (Container Registry)
- CloudWatch (Monitoring)
- ElastiCache (In-Memory Cache)
- OpenSearch (Search and Analytics)
- Route 53 (DNS and Domains)

## Features

- Intuitive user interface with selectors for each service
- Price calculation based on specific parameters for each service
- Display of summary table for all added resources
- Cost distribution chart
- Export of estimates in JSON format

## Setup

### Prerequisites

- Python 3.6+
- pip (Python package manager)

### Installation

1. Clone this repository
2. Create a virtual environment:
```bash
python -m venv venv
```
3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`
4. Install dependencies:
```bash
pip install streamlit boto3 pandas
```

### Running

To start the application, run:

```bash
streamlit run src/app.py
```

## Usage

1. Select an AWS service in the sidebar menu
2. Configure the specific parameters for the service
3. Click the "Add" button to include the resource in the calculator
4. Repeat steps 1-3 to add more resources
5. View the total cost and cost distribution
6. Export the results in JSON format if needed

## Notes

- This application does not connect directly to your AWS account
- Prices are approximate and may not reflect promotions, discounts, or specific agreements
- It does not include all possible costs, such as data transfer between regions, additional resources, or specific services

## Future Development

- Integration with the official AWS pricing API for more accurate values
- Addition of more AWS services
- Ability to save/load configurations
- Cost comparison between different regions
- Price estimates for complete architectures 