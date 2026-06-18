# sources/test-tools/kdevops/terraform/gce/scripts/gce_common.py

## Purpose
This module provides shared GCE helpers for Kconfig generators using direct Compute REST API calls with `google-auth` authorized sessions rather than the heavier `google-cloud-compute` SDK.

## Important APIs, Types, And Functions
`GceNotConfiguredError` marks optional auth absence. Constants define `GCE_COMPUTE_API` and `GCE_API_TIMEOUT`. `get_authenticated_session()` creates an OAuth-scoped `AuthorizedSession` and resolves project ID. `get_default_project()`, `get_default_region()`, and `get_default_zone()` read google-auth, environment variables, and gcloud config properties. `get_jinja2_environment()` enables Jinja loop controls. `load_yaml_config()` loads script-local YAML. Name helpers convert regions, zones, and machine types into Kconfig suffixes. REST list helpers include `list_regions()`, `list_zones()`, `list_machine_types()`, `list_machine_types_aggregated()`, `list_images()`, and `get_image_families()`. `require_gce_credentials()` wraps auth failures into `GceNotConfiguredError`.

## Control Flow
Generator scripts authenticate once, then pass the session and project to REST helpers. REST calls request limited fields, enforce a 30-second timeout, raise for most HTTP errors, and handle image-project 403/404 as empty lists. Pagination is handled for aggregated machine types and image lists. `get_image_families()` groups images by family, preferring non-deprecated and then newer images.

## State And Persistence
The module reads gcloud config, environment variables, and application-default credentials. It writes no files and maintains no cache. Remote GCE data is live state returned as plain dictionaries.

## Dependencies And Integration Points
It depends on `google-auth`, `requests`, `yaml`, `jinja2`, and Python typing/path/configparser modules. It is imported by GCE location, machine, and image generators. Generated outputs are sourced by `terraform/gce/Kconfig`.

## Risks And Test Signals
Project resolution can fail if application-default credentials lack a project and environment variables are unset. Direct REST calls require careful field selection and pagination; new API shapes can break assumptions. Image family selection compares ISO timestamp strings, which is acceptable for GCE timestamps but should be fixture-tested. Tests should mock authorized sessions for HTTP success, pagination, 403/404 image projects, auth failures, gcloud config reading, and Kconfig name conversion.
