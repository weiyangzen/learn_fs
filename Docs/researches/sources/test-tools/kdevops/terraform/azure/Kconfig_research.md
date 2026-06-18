# sources/test-tools/kdevops/terraform/azure/Kconfig

## Purpose
This Kconfig wrapper exposes Azure Terraform menus for location, compute size, OS image, storage, and identity/access when `TERRAFORM_AZURE` is enabled.

## Important APIs, Types, And Functions
It sources generated files `Kconfig.location.generated`, `Kconfig.size.generated`, and `Kconfig.image.generated`, plus static `Kconfig.storage` and `Kconfig.identity`. It uses comments to separate VM size and OS image selection under the compute menu.

## Control Flow
The file is guarded by `if TERRAFORM_AZURE`. Menu ordering is location, compute, storage, and identity/access.

## State And Persistence
Selected Azure symbols persist through Kconfig `.config` and generated YAML/Terraform variables. The wrapper has no state beyond the sourced menu tree.

## Dependencies And Integration Points
It depends on Azure dynamic generator scripts to populate generated Kconfig files and on Terraform Azure modules that consume those selections.

## Risks And Test Signals
Missing or stale generated files can break menu generation or offer invalid Azure choices. Tests should run Azure cloud-config generation with and without credentials, then run `olddefconfig`/menuconfig and verify selected symbols propagate into Terraform variables.
