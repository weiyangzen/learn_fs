# sources/test-tools/kdevops/terraform/Kconfig

## Purpose
This Kconfig fragment is the top-level Terraform configuration menu for kdevops when `TERRAFORM` is enabled. It wires provider-specific, SSH, private-network, and Terraform-vs-OpenTofu settings into generated YAML output.

## Important APIs, Types, And Functions
It sources `terraform/Kconfig.providers` and `terraform/Kconfig.ssh`, defines `TERRAFORM_PRIVATE_NET`, `TERRAFORM_PRIVATE_NET_PREFIX`, `TERRAFORM_PRIVATE_NET_MASK`, a choice between `TERRAFORM_USE_TERRAFORM` and `TERRAFORM_USE_OPENTOFU`, and `TERRAFORM_BINARY_PATH`. Several symbols use `output yaml` so generated configuration can feed automation.

## Control Flow
The whole file is guarded by `if TERRAFORM`. Provider and SSH menus are displayed first. Azure-only private network options follow, then a mutually exclusive IaC binary choice with Terraform as the default. The binary path default depends on the selected choice.

## State And Persistence
Kconfig choices persist in `.config` and downstream generated YAML. The binary path becomes a runtime dependency for Make/Terraform orchestration. Private-network prefix and mask persist as user-selected infrastructure configuration.

## Dependencies And Integration Points
It integrates with the broader kdevops Kconfig tree, provider-specific Terraform modules, YAML generation, and Make targets that invoke the configured Terraform/OpenTofu binary. `TERRAFORM_PRIVATE_NET` currently depends on Azure only.

## Risks And Test Signals
The default OpenTofu path `/usr/local/bin/tofu` may not match distro packaging. Private-network defaults can conflict with user networks. The Azure-only dependency should be retested if private networking becomes available for other providers. Test signals include `make menuconfig`, defconfig generation for Terraform and OpenTofu, YAML output inspection, and Make targets using the selected binary path.
