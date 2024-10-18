#!/usr/bin/env python3

import aws_cdk as cdk
from cdkapp.cdkapp_stack import CdkappStack

app = cdk.App()
CdkappStack(app, "CdkappStack")
app.synth()
