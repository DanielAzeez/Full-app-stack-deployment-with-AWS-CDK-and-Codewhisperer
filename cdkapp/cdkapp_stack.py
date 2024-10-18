from aws_cdk import (
    Duration,
    Stack,
    SecretValue,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_iam as iam,
    aws_elasticloadbalancingv2 as elbv2,
)
from constructs import Construct

class CdkappStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC with IpAddresses 10.10.0.0/16, a NAT gateway, a public subnet, PRIVATE_WITH_EGRESS subnet, and an RDS subnet
        vpc = ec2.Vpc(self, "MyVpc",
            ip_addresses=ec2.IpAddresses.cidr("10.10.0.0/16"),
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name="Public",
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    name="Private",
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    name="RDS",
                    cidr_mask=24
                )
            ]
        )
        
        # Create a security group for the load balancer
        lb_sg = ec2.SecurityGroup(self, "lb_sg",
            vpc=vpc,
            allow_all_outbound=True
        )
        
        # Create a security group for the RDS instance
        rds_sg = ec2.SecurityGroup(self, "rds_sg",
            vpc=vpc,
            allow_all_outbound=True
        )

        # Create a security group for the EC2 instances
        ec2_sg = ec2.SecurityGroup(self, "ec2_sg",
            vpc=vpc,
            allow_all_outbound=True
        )
        
        # Add ingress rules for the load balancer to allow all traffic
        lb_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))

        # Add ingress rule for the EC2 instances to allow 8443 traffic from the load balancer
        ec2_sg.add_ingress_rule(lb_sg, ec2.Port.tcp(8443))
        
        # Add ingress rule for the RDS instance to allow 3306 from the EC2 instances
        rds_sg.add_ingress_rule(ec2_sg, ec2.Port.tcp(3306))

        # Add ingress rule for the RDS instance to allow SSH (port 22) from the EC2 instances
        rds_sg.add_ingress_rule(ec2_sg, ec2.Port.tcp(22))
        
        # Create an RDS Aurora MySQL cluster
        cluster = rds.DatabaseCluster(self, "MyDatabase",
            engine=rds.DatabaseClusterEngine.aurora_mysql(version=rds.AuroraMysqlEngineVersion.VER_3_04_0),
            credentials=rds.Credentials.from_password("testuser", SecretValue.unsafe_plain_text("password1234!")),
            default_database_name="Population",
            instance_props={ 
                "vpc": vpc,
                "security_groups": [rds_sg],
                "vpc_subnets": ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)
            },
            instances=1
        )
        
        # Create an Amazon Linux 2 image
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2, 
            edition=ec2.AmazonLinuxEdition.STANDARD, 
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )
                        
        # Read userdata file from cdkapp directory
        with open("./cdkapp/userdata.sh") as f:
            userdata = f.read()
        
        # Create two t2.small EC2 instances in private subnets
        ec2_instance = ec2.Instance(self, "MyInstance",
            instance_type=ec2.InstanceType("t2.small"),
            machine_image=amzn_linux,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            availability_zone=vpc.availability_zones[0],
            user_data=ec2.UserData.custom(userdata),
            security_group=ec2_sg,
            role=iam.Role.from_role_name(self, "ec2_instance_role", "ec2_instance_role")
        )
        
        ec2_instance2 = ec2.Instance(self, "MyInstance2",
            instance_type=ec2.InstanceType("t2.small"),
            machine_image=amzn_linux,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            availability_zone=vpc.availability_zones[1],
            user_data=ec2.UserData.custom(userdata),
            security_group=ec2_sg,
            role=iam.Role.from_role_name(self, "ec2_instance_role2", "ec2_instance_role")
        )
        
        # Create a load balancer for the web servers
        lb = elbv2.ApplicationLoadBalancer(self, "MyLoadBalancer",
            vpc=vpc,
            internet_facing=True,
            security_group=lb_sg
        )

        # Create a listener for the load balancer
        listener = lb.add_listener("Listener",
            port=80,
            open=True
        )
            
        # Add EC2 instances as targets for the load balancer
        listener.add_targets("TargetGroup",
            port=80,
            targets=[ec2_instance, ec2_instance2]
        )
        
        # Add a dependency for the web server to wait for the RDS cluster
        ec2_instance.node.add_dependency(cluster)
        
        # Add a dependency for the listener to wait for the EC2 instances
        listener.node.add_dependency(ec2_instance)
