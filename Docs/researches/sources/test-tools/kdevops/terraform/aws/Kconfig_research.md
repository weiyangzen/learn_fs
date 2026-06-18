# sources/test-tools/kdevops/terraform/aws/Kconfig

## Purpose
This Kconfig fragment assembles AWS-specific Terraform configuration menus when `TERRAFORM_AWS` is selected.

## Important APIs, Types, And Functions
It creates menus for resource location, compute, storage, and identity/access. It sources wrapper/generated Kconfig files: `terraform/aws/kconfigs/Kconfig.location`, `Kconfig.instance`, `Kconfig.ami`, `Kconfig.storage`, and `Kconfig.identity`.

## Control Flow
The file is a declarative menu wrapper guarded by `if TERRAFORM_AWS`. Location is shown first, compute combines instance and AMI selection, then storage and identity menus are loaded.

## State And Persistence
The file itself has no runtime state. Selected symbols from sourced files persist in Kconfig `.config` and generated YAML/Terraform variable files.

## Dependencies And Integration Points
It depends on dynamic Kconfig generation targets such as `make cloud-config-aws` to populate current AWS location, instance, and AMI choices. It integrates with AWS Terraform modules and scripts under `terraform/aws/scripts`.

## Risks And Test Signals
Missing generated files can break menuconfig or hide choices. AWS resource availability changes frequently, so stale generated fragments can present unavailable AMIs, regions, or instance types. Tests should run menuconfig/olddefconfig before and after `make cloud-config-aws`, and validate that generated symbols match Terraform variable consumption.
