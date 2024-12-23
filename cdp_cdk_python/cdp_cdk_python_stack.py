from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_s3 as s3,
    aws_iam as iam,
    # aws_redshiftserverless as redshiftserverless,
    
)
import aws_cdk as core
from constructs import Construct

import os 
import json
from aws_cdk.cloudformation_include import CfnInclude

class CdpCdkPythonStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "CdpCdkPythonQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        # bucket = s3.Bucket(self, "MyFirstBucketTest", versioned=True)

        # Load parameters from a JSON file
        
        dirname = os.path.dirname(os.path.abspath(__file__))
        parameters_file = os.path.join(dirname, './mle-non-pii-redshift-role-param.json') 
        template_file = os.path.join(dirname, "./mle-non-pii-redshift-role-template.json")

        with open(parameters_file, "r") as f:
            parameters = json.load(f).get("parameters", "")
        print('DbUser: %s' % parameters["DbUser"]) 

        # Access parameters
        # dbUser = parameters.get("DbUser", "")
        # dbName = parameters.get("DbName", "")
        # Environment = parameters.get("Environment")

        # Include the existing CloudFormation template
        template = CfnInclude(
            self,
            "ExistingTemplate",
            template_file=template_file,
            parameters=parameters
        )
        
        # Pass the parameters to the template
        # template.add_parameter_override("DbUser", parameters["DbUser"])
        # template.add_parameter_override("DbName", parameters["DbName"])
        # template.add_parameter_override("Environment", parameters["Environment"])
        # template.add_parameter_override("ExternalAccountRootRoles", parameters["ExternalAccountRootRoles"])
        # template.add_parameter_override("ExternalIAMRoleARNs", parameters["ExternalIAMRoleARNs"])

# Access resources defined in the CloudFormation template
        redshiftCrossAccountRole = template.get_resource("RedshiftCrossAccountRole")

        # Create IAM role for Redshift access
        redshift_role = iam.Role(
            self, 
            "test-non-pii-RedshiftRole",
            assumed_by=iam.ServicePrincipal("redshift.amazonaws.com"),
        )

        redshift_role.attach_inline_policy(
            iam.Policy(
                self,
                "ExperimentationRedshiftPolicy",
                statements=[
                    iam.PolicyStatement(
                        actions=[
                            "redshift:GetClusterCredentials",
                            "redshift:CreateClusterUser"
                        ],
                        resources=[
                            "arn:aws:redshift:eu-west-1:977228593394:dbuser:test-idl-redshift-component-comp-redshiftcluster/experimentation_airflow",
                            "arn:aws:redshift:eu-west-1:977228593394:dbname:test-idl-redshift-component-comp-redshiftcluster/redshiftdb"
                        ],
                    )
                ],
            )
        )

        # # Create Redshift Serverless Namespace
        # namespace = redshiftserverless.CfnNamespace(
        #     self, "RedshiftNamespace",
        #     namespace_name="my-redshift-namespace",
        #     admin_username="admin",
        #     admin_user_password="YourSecurePassword123!",  # Use Secrets Manager for production
        #     iam_roles=[redshift_role.role_arn]
        # )

        # # Create Redshift Serverless Workgroup
        # workgroup = redshiftserverless.CfnWorkgroup(
        #     self, "RedshiftWorkgroup",
        #     workgroup_name="my-redshift-workgroup",
        #     namespace_name=namespace.namespace_name,
        #     base_capacity=32,  # Base capacity in Redshift Processing Units (RPUs)
        #     publicly_accessible=True,
        #     subnet_ids=["subnet-xxxxxxx", "subnet-yyyyyyy"],  # Replace with actual subnet IDs
        #     security_group_ids=["sg-zzzzzzzz"]  # Replace with actual security group IDs
        # )

        # core.CfnOutput(
        #     self, 
        #     "WorkgroupEndpoint", 
        #     value=workgroup.attr_endpoint_address)
        core.CfnOutput(
            self, 
            "RoleArn1", 
            value=f"arn:aws:iam:::{redshiftCrossAccountRole.ref}")
        core.CfnOutput(
            self, 
            "RoleArn2", 
            value=redshift_role.role_arn)
