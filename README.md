# Full-app-stack-deployment-with-AWS-CDK-and-Codewhisperer

This project demonstrates the creation and deployment of a full application stack using AWS Cloud Development Kit (CDK) for Infrastructure as Code (IaC) and Amazon CodeWhisperer for generative AI assistance in writing code. The infrastructure is built on AWS services, with an emphasis on deploying a secure and scalable web application that includes a load balancer, EC2 instances, and an RDS Aurora MySQL database.

The purpose of this project is to showcase how to automate the deployment of cloud infrastructure while adhering to best practices for high availability, security, and scalability.

## Key Components and Architecture

This project consists of the following key AWS components:

- **Amazon VPC (Virtual Private Cloud)**: The backbone network layer of the application, with isolated subnets for security.
- **Amazon EC2 (Elastic Compute Cloud)**: Two EC2 instances running Amazon Linux 2 to host the application, distributed across two availability zones for high availability.
- **Amazon RDS (Relational Database Service)**: An Aurora MySQL database cluster for storing application data, deployed in a private subnet for enhanced security.
- **Amazon ALB (Application Load Balancer)**: A load balancer to distribute incoming traffic between the two EC2 instances.
- **AWS CDK (Cloud Development Kit)**: Used to define and deploy the infrastructure as code.
- **Amazon CodeWhisperer**: A generative AI tool used to assist with code suggestions and optimization.
- **Security Groups**: Configured to allow secure communication between the various components and ensure that only necessary traffic is allowed.

The infrastructure is designed to be deployed in two availability zones to ensure fault tolerance and high availability. The web servers (EC2 instances) and the database (RDS) are hosted in different subnets (public and private respectively), and a NAT gateway is used to allow the EC2 instances to access the internet without exposing them to public access.

### Project Features

1. **Automated Infrastructure Deployment**: The entire infrastructure is created and managed using AWS CDK, eliminating the need for manual setup of resources.
2. **Load Balancing and High Availability**: Traffic is distributed across two EC2 instances located in different availability zones using an Application Load Balancer (ALB).
3. **Secure Network Architecture**: Security groups are configured to allow the minimum necessary access, ensuring secure communication between services. The RDS instance is kept in a private subnet for additional protection.
4. **Scalability**: The architecture is designed to allow future scaling of both EC2 instances and the RDS database, providing flexibility for growing workloads.
5. **Generative AI Assistance**: Amazon CodeWhisperer was used to generate portions of the infrastructure code, demonstrating how AI can assist in automating cloud deployments.

## Detailed Project Structure

Here is an in-depth explanation of the project’s structure, including all components and how they interact:

### 1. **Virtual Private Cloud (VPC)**

The VPC forms the network backbone for the infrastructure. It has three subnet groups:
- **Public Subnet**: Hosts the Application Load Balancer (ALB).
- **Private Subnet (with Egress)**: Hosts the EC2 instances, which can communicate with the internet through a NAT gateway.
- **Private Subnet (Isolated)**: Hosts the Aurora MySQL RDS cluster, which is isolated from direct internet access for enhanced security.

The VPC uses the IP range `10.10.0.0/16` and is deployed across two availability zones to ensure high availability.

### 2. **EC2 Instances**

Two Amazon EC2 instances, each running Amazon Linux 2, are created to serve as web servers. They are located in the private subnet, making them inaccessible from the public internet directly. Instead, they are fronted by the Application Load Balancer, which routes traffic to the instances. The instances run the necessary user data script to install web server software and start the application.

### 3. **Application Load Balancer (ALB)**

The Application Load Balancer is deployed in the public subnet and routes HTTP traffic to the EC2 instances. It serves as the entry point for the web application and evenly distributes incoming traffic between the two instances to ensure load balancing and high availability. The listener on port 80 forwards requests to the target group containing the EC2 instances.

### 4. **Aurora MySQL Database**

Amazon RDS Aurora is used to provide a scalable, managed MySQL database for the application. The RDS instance is deployed in a private isolated subnet, ensuring it is not exposed to the internet. The database is configured with automated backups and failover to ensure durability and availability.

### 5. **Security Configuration**

The project includes multiple security groups to control network access:

- **EC2 Security Group**: Allows incoming traffic from the Application Load Balancer (port 80) and SSH access (port 22) from trusted IPs.
- **ALB Security Group**: Allows incoming HTTP traffic from the internet (port 80) and forwards it to the EC2 instances.
- **RDS Security Group**: Restricts access to the database to only the EC2 instances over MySQL’s default port (3306).

### 6. **Infrastructure as Code with AWS CDK**

The AWS CDK is used to define all infrastructure components programmatically. The CDK stack includes:
- **VPC**: Configuration for the subnets and NAT gateway.
- **EC2 Instances**: Configuration for instance types, security groups, and user data scripts.
- **RDS Database**: Configuration for the Aurora MySQL cluster, database credentials, and backup settings.
- **ALB**: Configuration for the load balancer and its listener.

Code for the stack is located in `cdkapp/cdkapp_stack.py`.

### 7. **Generative AI with Amazon CodeWhisperer**

Amazon CodeWhisperer was integrated into the project to provide AI-driven suggestions while writing infrastructure code. This enhanced productivity and ensured that the best practices were followed, particularly in managing complex configurations for the load balancer, EC2 instances, and RDS setup.

## How to Deploy the Project

### Prerequisites

To deploy this project, ensure you have the following:

1. **AWS Account**: You must have an AWS account with sufficient privileges to create VPCs, EC2 instances, RDS databases, and other resources.
2. **AWS CDK Installed**: The AWS CDK must be installed on your local machine. You can install it using the following command:
   ```bash
   npm install -g aws-cdk
   ```
3. **AWS CLI Configured**: Ensure that your AWS CLI is configured with appropriate access credentials:
   ```bash
   aws configure
   ```

### Steps to Deploy

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/cloud-infrastructure-with-aws-cdk
   cd cloud-infrastructure-with-aws-cdk
   ```

2. **Install Dependencies**:
   Navigate to the `cdkapp/` directory and install the required dependencies for the CDK app:
   ```bash
   pip install -r requirements.txt
   ```

3. **Bootstrap the Environment**:
   If this is your first time deploying CDK into the AWS account, you'll need to bootstrap it:
   ```bash
   cdk bootstrap
   ```

4. **Deploy the Stack**:
   Deploy the CDK stack to create the infrastructure in your AWS account:
   ```bash
   cdk deploy
   ```

5. **Access the Application**:
   After the deployment completes, the Application Load Balancer URL will be provided in the terminal. You can access the application by navigating to this URL in your browser.

## Troubleshooting

- Ensure that your AWS account has sufficient permissions to create all resources.
- Check that your AWS CLI is properly configured with the right region and credentials.
- If deployment fails, verify that your security groups are configured correctly and that all dependencies are installed.
