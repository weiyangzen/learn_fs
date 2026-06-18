# sources/test-tools/kdevops/terraform/aws/scripts/aws_common.py

## Purpose
This module provides shared AWS helper functions for scripts that generate AWS Kconfig menus for regions, availability zones, instance types, and AMIs.

## Important APIs, Types, And Functions
`AwsNotConfiguredError` signals optional missing credentials. `get_default_region()` reads `~/.aws/config` and falls back to `us-east-1`. `get_jinja2_environment()` creates a trimmed/lstripped Jinja2 environment rooted at the caller script directory. `create_ec2_client()` builds a boto3 EC2 client. `handle_aws_client_error()` and `handle_aws_credentials_error()` provide common stderr messages. `require_aws_credentials()` validates credentials using STS caller identity. `get_all_regions()` calls `describe_regions(AllRegions=True)`. `get_region_availability_zones()` calls `describe_availability_zones()` for availability-zone types. `get_all_instance_types()` pages through `describe_instance_types()`. `get_region_kconfig_name()` converts region names to Kconfig symbol suffixes.

## Control Flow
Generator scripts call `require_aws_credentials()` early when live AWS data is needed, then use the list/query helpers and Jinja environment. Query helpers catch credential and client errors and return empty lists or `None` rather than throwing, allowing callers to choose whether to exit or skip optional generation.

## State And Persistence
The module reads `~/.aws/config` but writes no state. AWS credential/session state is managed by boto3. Returned data structures are in-memory lists and dictionaries consumed by Kconfig renderers.

## Dependencies And Integration Points
It depends on `boto3`, `botocore`, `jinja2`, and Python `ConfigParser`. It is imported by AWS `gen_kconfig_location`, `gen_kconfig_instance`, and `gen_kconfig_ami`. It integrates with local AWS CLI/profile conventions without shelling out to `aws`.

## Risks And Test Signals
`require_aws_credentials()` uses STS without explicitly passing the default region, so unusual profiles may fail differently from EC2 calls. `get_default_region()` supports common default profile names but not all AWS config inheritance features. Client helpers return empty results on broad exceptions, which can hide transient API failures. Tests should mock boto3 clients/paginators for success/error paths, parse sample config files, verify Kconfig name conversion, and ensure generators skip cleanly when credentials are absent.
