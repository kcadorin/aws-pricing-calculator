import streamlit as st
import pandas as pd
import boto3
from datetime import datetime, timedelta
from aws_services import estimate_price
import json


# Helper function to format quantity with units
def format_quantity(service, quantity):
    if service == "EC2":
        return f"{quantity} (instances)"
    elif service == "S3":
        return f"{quantity} (GB)"
    elif service == "Lambda":
        return f"{quantity:.0f} (GB-seconds)"
    elif service == "Fargate/ECS":
        return f"{quantity} (hours/month)"
    elif service == "ElastiCache":
        return f"{quantity} (nodes)"
    elif service == "ECR":
        return f"{quantity} (GB)"
    elif service == "OpenSearch":
        return f"{quantity} (instances)"
    elif service == "Route 53":
        return f"{quantity} (hosted zones)"
    elif service == "CloudWatch":
        return f"{quantity} (service)"
    else:
        return str(quantity)


# Function to get the current AWS costs from Cost Explorer
def get_aws_current_costs(days=30, profile_name=None):
    """
    Get the current costs from AWS Cost Explorer for the given period.

    Parameters:
    - days: Number of days to look back (default: 30)
    - profile_name: AWS profile name to use (default: None, uses default profile)

    Returns:
    - Dictionary with cost data by service
    """
    try:
        # Create a session using the specified profile or default
        if profile_name:
            session = boto3.Session(profile_name=profile_name)
        else:
            session = boto3.Session()

        # Create Cost Explorer client
        ce_client = session.client("ce")

        # Calculate start and end dates
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # Format dates as strings
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        # Get cost and usage data
        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date_str, "End": end_date_str},
            Granularity="MONTHLY",
            Metrics=["BlendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )

        # Process the response
        service_costs = {}
        if "ResultsByTime" in response and len(response["ResultsByTime"]) > 0:
            for group in response["ResultsByTime"][0]["Groups"]:
                service_name = group["Keys"][0]
                cost = float(group["Metrics"]["BlendedCost"]["Amount"])
                service_costs[service_name] = cost

        return {
            "success": True,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "costs": service_costs,
            "total": sum(service_costs.values()),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


st.set_page_config(page_title="AWS Cost Calculator", page_icon="💰", layout="wide")

# Initialize session state for selected resources
if "resources" not in st.session_state:
    st.session_state.resources = []

# Initialize session state for current AWS costs
if "current_costs" not in st.session_state:
    st.session_state.current_costs = None

# Application title
st.title("AWS Cost Calculator 💰")

# Sidebar for service selection
st.sidebar.header("Select AWS Services")

service_options = {
    "EC2": "AmazonEC2",
    "S3": "AmazonS3",
    "Fargate/ECS": "AmazonECS",
    "Lambda": "AWSLambda",
    "ECR": "AmazonECR",
    "CloudWatch": "AmazonCloudWatch",
    "ElastiCache": "AmazonElastiCache",
    "OpenSearch": "AmazonOpenSearch",
    "Route 53": "AmazonRoute53",
}

selected_service = st.sidebar.selectbox("AWS Service", list(service_options.keys()))

# Main interface based on selected service
st.header(f"Configure {selected_service}")

# Specific logic for each service
if selected_service == "EC2":
    # Configuration for EC2
    instance_types = [
        # General Purpose
        "t3.nano",
        "t3.micro",
        "t3.small",
        "t3.medium",
        "t3.large",
        "t3.xlarge",
        "t3.2xlarge",
        "t4g.nano",
        "t4g.micro",
        "t4g.small",
        "t4g.medium",
        "t4g.large",
        "t4g.xlarge",
        "t4g.2xlarge",
        "m5.large",
        "m5.xlarge",
        "m5.2xlarge",
        "m5.4xlarge",
        "m5.8xlarge",
        "m5.12xlarge",
        "m5.16xlarge",
        "m5.24xlarge",
        "m6g.medium",
        "m6g.large",
        "m6g.xlarge",
        "m6g.2xlarge",
        "m6g.4xlarge",
        "m6g.8xlarge",
        "m6g.12xlarge",
        "m6g.16xlarge",
        # Compute Optimized
        "c5.large",
        "c5.xlarge",
        "c5.2xlarge",
        "c5.4xlarge",
        "c5.9xlarge",
        "c5.12xlarge",
        "c5.18xlarge",
        "c5.24xlarge",
        "c6g.medium",
        "c6g.large",
        "c6g.xlarge",
        "c6g.2xlarge",
        "c6g.4xlarge",
        "c6g.8xlarge",
        "c6g.12xlarge",
        "c6g.16xlarge",
        # Memory Optimized
        "r5.large",
        "r5.xlarge",
        "r5.2xlarge",
        "r5.4xlarge",
        "r5.8xlarge",
        "r5.12xlarge",
        "r5.16xlarge",
        "r5.24xlarge",
        "r6g.medium",
        "r6g.large",
        "r6g.xlarge",
        "r6g.2xlarge",
        "r6g.4xlarge",
        "r6g.8xlarge",
        "r6g.12xlarge",
        "r6g.16xlarge",
        # Accelerated Computing
        "p3.2xlarge",
        "p3.8xlarge",
        "p3.16xlarge",
        "g4dn.xlarge",
        "g4dn.2xlarge",
        "g4dn.4xlarge",
        "g4dn.8xlarge",
        "g4dn.16xlarge",
    ]

    # Use a select box with adjustable height
    instance_type = st.selectbox(
        "Instance Type", instance_types, help="Select the EC2 instance type"
    )

    regions = ["us-east-1", "us-west-2", "eu-west-1", "sa-east-1"]
    region = st.selectbox("Region", regions)

    os_options = ["Linux", "Windows"]
    os_type = st.selectbox("Operating System", os_options)

    quantity = st.number_input("Number of Instances", min_value=1, value=1)
    hours_per_day = st.slider("Hours per Day", 1, 24, 24)
    days_per_month = st.slider("Days per Month", 1, 31, 30)

    if st.button("Add EC2 to Calculator"):
        params = {
            "instance_type": instance_type,
            "region": region,
            "os_type": os_type,
            "quantity": quantity,
            "hours_per_day": hours_per_day,
            "days_per_month": days_per_month,
        }

        # Get price estimate
        price_data = estimate_price("EC2", params)

        resource = {
            "service": "EC2",
            "details": f"{instance_type} ({region}, {os_type})",
            "quantity": quantity,
            "unit_price": price_data["unit_price"],
            "monthly_hours": price_data["monthly_hours"],
            "total_price": price_data["total_price"],
        }

        st.session_state.resources.append(resource)
        st.success(f"Added {quantity} {instance_type} instances to calculator!")

elif selected_service == "S3":
    # Configuration for S3
    storage_gb = st.number_input("Storage (GB)", min_value=1, value=100)

    storage_class = st.selectbox(
        "Storage Class",
        [
            "Standard",
            "Intelligent-Tiering",
            "Standard-IA",
            "One Zone-IA",
            "Glacier",
            "Glacier Deep Archive",
        ],
    )

    regions = ["us-east-1", "us-west-2", "eu-west-1", "sa-east-1"]
    region = st.selectbox("Region", regions)

    if st.button("Add S3 to Calculator"):
        params = {
            "storage_gb": storage_gb,
            "storage_class": storage_class,
            "region": region,
        }

        # Get price estimate
        price_data = estimate_price("S3", params)

        resource = {
            "service": "S3",
            "details": f"{storage_class} ({region})",
            "quantity": storage_gb,
            "unit_price": price_data["unit_price"],
            "monthly_hours": 1,  # Not relevant for S3
            "total_price": price_data["total_price"],
        }

        st.session_state.resources.append(resource)
        st.success(
            f"Added {storage_gb} GB of S3 {storage_class} storage to calculator!"
        )

elif selected_service == "Lambda":
    # Configuration for Lambda
    requests_millions = st.number_input(
        "Number of Requests (millions per month)", min_value=0.1, value=1.0, step=0.1
    )

    # Improve memory options display
    memory_options = [128, 256, 512, 1024, 2048, 4096, 8192, 10240]
    memory_mb = st.select_slider("Memory (MB)", options=memory_options, value=128)

    avg_duration_ms = st.number_input("Average Duration (ms)", min_value=1, value=100)

    regions = ["us-east-1", "us-west-2", "eu-west-1", "sa-east-1"]
    region = st.selectbox("Region", regions)

    if st.button("Add Lambda to Calculator"):
        params = {
            "requests": requests_millions,
            "memory": memory_mb,
            "avg_duration": avg_duration_ms,
            "region": region,
        }

        # Get price estimate
        price_data = estimate_price("Lambda", params)

        gb_factor = memory_mb / 1024
        seconds_per_invocation = avg_duration_ms / 1000

        resource = {
            "service": "Lambda",
            "details": f"{memory_mb}MB, {avg_duration_ms}ms, {requests_millions}M requests ({region})",
            "quantity": price_data["quantity"],
            "unit_price": price_data["unit_price"],
            "monthly_hours": 1,  # Not relevant for Lambda
            "total_price": price_data["total_price"],
        }

        st.session_state.resources.append(resource)
        st.success(f"Added Lambda function with {memory_mb}MB memory to calculator!")

elif selected_service == "Fargate/ECS":
    # Configuration for Fargate
    vcpu = st.number_input(
        "vCPUs", min_value=0.25, max_value=16.0, value=1.0, step=0.25
    )
    memory_gb = st.number_input(
        "Memory (GB)", min_value=0.5, max_value=120.0, value=2.0, step=0.5
    )
    hours_per_day = st.slider("Hours per Day", 1, 24, 24)
    days_per_month = st.slider("Days per Month", 1, 31, 30)

    regions = ["us-east-1", "us-west-2", "eu-west-1", "sa-east-1"]
    region = st.selectbox("Region", regions)

    if st.button("Add Fargate to Calculator"):
        hours_per_month = hours_per_day * days_per_month

        params = {
            "vcpu": vcpu,
            "memory_gb": memory_gb,
            "hours_per_month": hours_per_month,
            "region": region,
        }

        # Get price estimate
        price_data = estimate_price("Fargate/ECS", params)

        resource = {
            "service": "Fargate/ECS",
            "details": f"{vcpu} vCPU, {memory_gb}GB RAM ({region})",
            "quantity": hours_per_month,
            "unit_price": price_data["unit_price"],
            "monthly_hours": hours_per_month,
            "total_price": price_data["total_price"],
        }

        st.session_state.resources.append(resource)
        st.success(
            f"Added Fargate cluster with {vcpu} vCPUs and {memory_gb}GB memory to calculator!"
        )

elif selected_service == "CloudWatch":
    # Configuration for CloudWatch
    ingestion_gb = st.number_input("Log Ingestion (GB/month)", min_value=1, value=10)
    storage_gb = st.number_input("Log Storage (GB)", min_value=1, value=10)
    metrics = st.number_input("Custom Metrics", min_value=0, value=10)
    alarms = st.number_input("Alarms", min_value=0, value=5)
    dashboards = st.number_input("Dashboards", min_value=0, value=1)

    if st.button("Add CloudWatch to Calculator"):
        params = {
            "ingestion_gb": ingestion_gb,
            "storage_gb": storage_gb,
            "metrics": metrics,
            "alarms": alarms,
            "dashboards": dashboards,
        }

        # Get price estimate
        price_data = estimate_price("CloudWatch", params)

        resource = {
            "service": "CloudWatch",
            "details": f"{ingestion_gb}GB logs, {metrics} metrics, {alarms} alarms, {dashboards} dashboards",
            "quantity": 1,
            "unit_price": price_data["total_price"],
            "monthly_hours": 1,
            "total_price": price_data["total_price"],
        }

        st.session_state.resources.append(resource)
        st.success(f"Added CloudWatch to calculator!")

elif selected_service == "ElastiCache":
    # Configuration for ElastiCache
    node_types = [
        "cache.t3.micro",
        "cache.t3.small",
        "cache.t3.medium",
        "cache.m5.large",
        "cache.r5.large",
    ]
    node_type = st.selectbox("Node Type", node_types)
    nodes = st.number_input("Number of Nodes", min_value=1, value=1)
    hours_per_day = st.slider("Hours per Day", 1, 24, 24)
    days_per_month = st.slider("Days per Month", 1, 31, 30)

    regions = ["us-east-1", "us-west-2", "eu-west-1", "sa-east-1"]
    region = st.selectbox("Region", regions)

    if st.button("Add ElastiCache to Calculator"):
        hours = hours_per_day * days_per_month

        params = {
            "node_type": node_type,
            "nodes": nodes,
            "hours": hours,
            "region": region,
        }

        # Get price estimate
        price_data = estimate_price("ElastiCache", params)

        resource = {
            "service": "ElastiCache",
            "details": f"{nodes} nodes {node_type} ({region})",
            "quantity": nodes,
            "unit_price": price_data["unit_price"],
            "monthly_hours": hours,
            "total_price": price_data["total_price"],
        }

        st.session_state.resources.append(resource)
        st.success(f"Added {nodes} ElastiCache {node_type} nodes to calculator!")

elif selected_service == "ECR":
    # Configuration for ECR
    storage_gb = st.number_input("Storage (GB/month)", min_value=1, value=10)
    data_transfer_gb = st.number_input(
        "Data Transfer (GB/month)", min_value=0, value=50
    )

    if st.button("Add ECR to Calculator"):
        params = {
            "storage_gb": storage_gb,
            "data_transfer_gb": data_transfer_gb,
        }

        # Get price estimate
        price_data = estimate_price("ECR", params)

        resource = {
            "service": "ECR",
            "details": f"{storage_gb}GB storage, {data_transfer_gb}GB data transfer",
            "quantity": storage_gb,
            "unit_price": price_data["unit_price"],
            "monthly_hours": 1,
            "total_price": price_data["total_price"],
        }

        st.session_state.resources.append(resource)
        st.success(f"Added ECR with {storage_gb}GB storage to calculator!")

elif selected_service == "OpenSearch":
    # Configuration for OpenSearch
    instance_types = [
        "t3.small.search",
        "t3.medium.search",
        "m5.large.search",
        "c5.large.search",
    ]
    instance_type = st.selectbox("Instance Type", instance_types)
    instances = st.number_input("Number of Instances", min_value=1, value=1)
    storage_gb = st.number_input("Storage (GB)", min_value=10, value=10)

    regions = ["us-east-1", "us-west-2", "eu-west-1", "sa-east-1"]
    region = st.selectbox("Region", regions)

    if st.button("Add OpenSearch to Calculator"):
        params = {
            "instance_type": instance_type,
            "instances": instances,
            "storage_gb": storage_gb,
            "region": region,
        }

        # Get price estimate
        price_data = estimate_price("OpenSearch", params)

        resource = {
            "service": "OpenSearch",
            "details": f"{instances} instances {instance_type}, {storage_gb}GB ({region})",
            "quantity": instances,
            "unit_price": price_data["unit_price"],
            "monthly_hours": 730,  # ~30 days
            "total_price": price_data["total_price"],
        }

        st.session_state.resources.append(resource)
        st.success(
            f"Added OpenSearch with {instances} {instance_type} instances to calculator!"
        )

elif selected_service == "Route 53":
    # Configuration for Route 53
    hosted_zones = st.number_input("Hosted Zones", min_value=1, value=1)
    queries_millions = st.number_input(
        "DNS Queries (millions per month)", min_value=0.1, value=1.0, step=0.1
    )

    if st.button("Add Route 53 to Calculator"):
        params = {
            "hosted_zones": hosted_zones,
            "queries_millions": queries_millions,
        }

        # Get price estimate
        price_data = estimate_price("Route 53", params)

        resource = {
            "service": "Route 53",
            "details": f"{hosted_zones} zones, {queries_millions}M queries/month",
            "quantity": hosted_zones,
            "unit_price": price_data["unit_price"],
            "monthly_hours": 1,
            "total_price": price_data["total_price"],
        }

        st.session_state.resources.append(resource)
        st.success(f"Added Route 53 with {hosted_zones} hosted zones to calculator!")

# Display table of added resources
st.header("Selected Resources")

if st.session_state.resources:
    # Create DataFrame for display
    df = pd.DataFrame(st.session_state.resources)

    # Rename columns to English
    df = df.rename(
        columns={
            "service": "Service",
            "details": "Details",
            "quantity": "Quantity",
            "unit_price": "Unit Price (USD)",
            "monthly_hours": "Monthly Hours",
            "total_price": "Total Price (USD)",
        }
    )

    # Create a copy of the DataFrame for display
    display_df = df[
        [
            "Service",
            "Details",
            "Quantity",
            "Unit Price (USD)",
            "Total Price (USD)",
        ]
    ].copy()  # Use copy to avoid SettingWithCopyWarning

    # Create a new column for formatted quantity instead of modifying the original
    display_df["Formatted Quantity"] = display_df.apply(
        lambda row: format_quantity(row["Service"], row["Quantity"]), axis=1
    )

    # Drop the original Quantity column and rename the formatted one
    display_df = display_df.drop(columns=["Quantity"])
    display_df = display_df.rename(columns={"Formatted Quantity": "Quantity"})

    # Ensure numeric columns are float type first - only for price columns
    display_df["Unit Price (USD)"] = pd.to_numeric(
        display_df["Unit Price (USD)"], errors="coerce"
    )
    display_df["Total Price (USD)"] = pd.to_numeric(
        display_df["Total Price (USD)"], errors="coerce"
    )

    # Format currency columns using a safer approach
    display_df["Unit Price (USD)"] = display_df["Unit Price (USD)"].apply(
        lambda x: f"${x:.4f}"
    )
    display_df["Total Price (USD)"] = display_df["Total Price (USD)"].apply(
        lambda x: f"${x:.2f}"
    )

    # Display the table
    st.dataframe(display_df)

    # Add explanation for quantity values
    st.markdown(
        """
    **Understanding the Quantity Values:**
    - **EC2**: Number of instances
    - **S3**: Storage in GB
    - **Lambda**: GB-seconds
    - **Fargate/ECS**: Hours per month
    - **ElastiCache**: Number of nodes
    - **ECR**: Storage in GB
    - **OpenSearch**: Number of instances
    - **Route 53**: Number of hosted zones
    """
    )

    # Calculate and display total
    total_cost = sum(resource["total_price"] for resource in st.session_state.resources)
    st.subheader(f"Estimated Monthly Total Cost: ${total_cost:.2f}")

    # Add pie chart for cost distribution of new resources
    if len(st.session_state.resources) > 1:
        st.subheader("New Resources Cost Distribution")

        # Prepare data for chart
        services = [resource["service"] for resource in st.session_state.resources]
        costs = [resource["total_price"] for resource in st.session_state.resources]

        # Create DataFrame for chart
        chart_data = pd.DataFrame({"Service": services, "Cost": costs})

        # Use plotly for pie chart instead of deprecated st.pie_chart
        try:
            import plotly.express as px

            fig = px.pie(
                chart_data,
                values="Cost",
                names="Service",
                title="Cost Distribution by Service",
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.warning(
                "Plotly is not installed. To view the pie chart, install it with: pip install plotly"
            )
            # Show as bar chart instead
            st.bar_chart(chart_data.set_index("Service"))

    # Compare with current AWS costs
    st.header("Compare with Current AWS Costs")

    # Create an expander for AWS credentials
    with st.expander("AWS Cost Explorer Settings"):
        st.info(
            "To use this feature, you need AWS Cost Explorer enabled in your account and appropriate permissions."
        )
        st.markdown(
            """
        **Required permissions:**
        - `ce:GetCostAndUsage`
        - `ce:GetDimensionValues`
        
        You can use your default AWS profile or enter a specific profile name.
        """
        )

        # AWS Profile selection
        use_default_profile = st.checkbox("Use Default AWS Profile", value=True)
        profile_name = (
            None if use_default_profile else st.text_input("AWS Profile Name")
        )

        # Date range selection
        days_options = [30, 60, 90]
        days_back = st.selectbox("Days to Analyze", days_options, index=0)

        # Button to fetch costs
        fetch_costs = st.button("Fetch Current AWS Costs")

    if fetch_costs:
        with st.spinner("Fetching AWS costs..."):
            current_costs = get_aws_current_costs(
                days=days_back, profile_name=profile_name
            )

            if current_costs["success"]:
                st.session_state.current_costs = current_costs
                st.success(
                    f"Successfully fetched AWS costs from {current_costs['start_date']} to {current_costs['end_date']}"
                )
            else:
                st.error(f"Failed to fetch AWS costs: {current_costs['error']}")
                st.markdown(
                    """
                **Common issues:**
                - Missing AWS credentials
                - Insufficient permissions
                - Cost Explorer not enabled in your account
                
                Please check your AWS configuration and try again.
                """
                )

    # Display comparison if we have current costs
    if st.session_state.get("current_costs") and st.session_state.resources:
        current_costs = st.session_state.current_costs

        # Create a comparison table
        st.subheader("Cost Comparison")

        current_total = current_costs["total"]
        new_total = total_cost
        total_with_new = current_total + new_total
        increase_percentage = (
            (new_total / current_total * 100) if current_total > 0 else 0
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Current Monthly Cost", f"${current_total:.2f}")
        col2.metric("New Resources Cost", f"${new_total:.2f}")
        col3.metric(
            "Total Projected Cost",
            f"${total_with_new:.2f}",
            f"+{increase_percentage:.1f}%",
        )

        # Create detailed comparison by service
        st.subheader("Cost Breakdown")

        # Map AWS service names to our internal service names
        service_name_mapping = {
            "Amazon Elastic Compute Cloud - Compute": "EC2",
            "Amazon Simple Storage Service": "S3",
            "AWS Lambda": "Lambda",
            "Amazon Elastic Container Service": "Fargate/ECS",
            "Amazon Elastic Container Registry": "ECR",
            "Amazon CloudWatch": "CloudWatch",
            "Amazon ElastiCache": "ElastiCache",
            "Amazon OpenSearch Service": "OpenSearch",
            "Amazon Route 53": "Route 53",
        }

        # Create a dictionary with current costs by service (using our internal names)
        current_costs_by_service = {}
        for aws_service, cost in current_costs["costs"].items():
            # Try to map the AWS service name to our internal name
            for aws_name, internal_name in service_name_mapping.items():
                if aws_name in aws_service:
                    if internal_name not in current_costs_by_service:
                        current_costs_by_service[internal_name] = 0
                    current_costs_by_service[internal_name] += cost
                    break
            else:
                # If no mapping found, use the AWS service name
                if aws_service not in current_costs_by_service:
                    current_costs_by_service[aws_service] = 0
                current_costs_by_service[aws_service] += cost

        # Create a dictionary with new costs by service
        new_costs_by_service = {}
        for resource in st.session_state.resources:
            service = resource["service"]
            if service not in new_costs_by_service:
                new_costs_by_service[service] = 0
            new_costs_by_service[service] += resource["total_price"]

        # Combine all services from both dictionaries
        all_services = set(
            list(current_costs_by_service.keys()) + list(new_costs_by_service.keys())
        )

        # Create comparison data
        comparison_data = []
        for service in all_services:
            current_cost = current_costs_by_service.get(service, 0)
            new_cost = new_costs_by_service.get(service, 0)
            total_cost = current_cost + new_cost
            increase = (
                new_cost / current_cost * 100 if current_cost > 0 else float("inf")
            )

            comparison_data.append(
                {
                    "Service": service,
                    "Current Cost (USD)": current_cost,
                    "New Resources (USD)": new_cost,
                    "Total Cost (USD)": total_cost,
                    "Increase (%)": increase if increase != float("inf") else None,
                }
            )

        # Sort by total cost (descending)
        comparison_data.sort(key=lambda x: x["Total Cost (USD)"], reverse=True)

        # Create DataFrame
        df_comparison = pd.DataFrame(comparison_data)

        # Format currency and percentage columns
        # Primeiro, criamos cópias das colunas originais antes de formatar
        formatted_cols = {}
        for col in ["Current Cost (USD)", "New Resources (USD)", "Total Cost (USD)"]:
            formatted_cols[col] = df_comparison[col].apply(lambda x: f"${x:.2f}")

        # Formatar a coluna de percentual
        formatted_cols["Increase (%)"] = df_comparison["Increase (%)"].apply(
            lambda x: f"{x:.1f}%" if x is not None else "N/A"
        )

        # Criar um novo DataFrame apenas com os valores formatados
        display_df_comparison = pd.DataFrame(
            {
                "Service": df_comparison["Service"],
                "Current Cost (USD)": formatted_cols["Current Cost (USD)"],
                "New Resources (USD)": formatted_cols["New Resources (USD)"],
                "Total Cost (USD)": formatted_cols["Total Cost (USD)"],
                "Increase (%)": formatted_cols["Increase (%)"],
            }
        )

        # Display the table
        st.dataframe(display_df_comparison)

        # Create visualization
        try:
            import plotly.express as px

            # Prepare data for visualization
            viz_data = []
            for item in comparison_data:
                service = item["Service"]
                current_cost = item[
                    "Current Cost (USD)"
                ]  # Valores originais, não formatados
                new_cost = item[
                    "New Resources (USD)"
                ]  # Valores originais, não formatados

                if current_cost > 0:
                    viz_data.append(
                        {
                            "Service": service,
                            "Cost Type": "Current",
                            "Cost": current_cost,
                        }
                    )
                if new_cost > 0:
                    viz_data.append(
                        {"Service": service, "Cost Type": "New", "Cost": new_cost}
                    )

            # Create DataFrame
            df_viz = pd.DataFrame(viz_data)

            # Create stacked bar chart
            fig = px.bar(
                df_viz,
                x="Service",
                y="Cost",
                color="Cost Type",
                title="Cost Comparison by Service",
                barmode="stack",
                labels={"Cost": "Cost (USD)"},
                color_discrete_map={"Current": "#1f77b4", "New": "#ff7f0e"},
            )

            st.plotly_chart(fig, use_container_width=True)

        except ImportError:
            st.warning(
                "Plotly is not installed. To view the visualization, install it with: pip install plotly"
            )

            # Simple bar chart using Streamlit
            chart_data = pd.DataFrame(
                {
                    "Service": [item["Service"] for item in comparison_data],
                    "Current": [item["Current Cost (USD)"] for item in comparison_data],
                    "New": [item["New Resources (USD)"] for item in comparison_data],
                }
            ).set_index("Service")

            st.bar_chart(chart_data)

    if st.button("Clear All Resources"):
        st.session_state.resources = []
        st.experimental_rerun()
else:
    st.info(
        "No resources added. Use the panel on the left to add AWS resources to your calculator."
    )

# Add option to export results
if st.session_state.resources:
    st.header("Export Results")

    export_data = {
        "resources": st.session_state.resources,
        "total_cost": sum(
            resource["total_price"] for resource in st.session_state.resources
        ),
    }

    # Convert to JSON
    export_json = json.dumps(export_data, indent=4)

    st.download_button(
        label="Download Estimate as JSON",
        data=export_json,
        file_name="aws_cost_estimate.json",
        mime="application/json",
    )

# Footer
st.markdown("---")
st.markdown(
    "**Note:** This is a simplified estimate calculator. Actual prices may vary based on specific usage details, promotions, corporate agreements, and other factors."
)
