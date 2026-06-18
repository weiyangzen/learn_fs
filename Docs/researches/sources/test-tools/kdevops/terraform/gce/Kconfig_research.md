# sources/test-tools/kdevops/terraform/gce/Kconfig

## Purpose
This Kconfig wrapper exposes GCE Terraform menus for resource location, machine type, OS image, storage, and identity/access when `TERRAFORM_GCE` is enabled.

## Important APIs, Types, And Functions
It sources generated files `Kconfig.location.generated`, `Kconfig.machine.generated`, and `Kconfig.image.generated`, plus static `Kconfig.storage` and `Kconfig.identity`. Compute is split into machine and OS image selection comments.

## Control Flow
The file is declarative and guarded by `if TERRAFORM_GCE`. Menu order is location, compute, storage, then identity/access.

## State And Persistence
Selected GCE symbols persist in Kconfig `.config` and generated Terraform/YAML configuration. The wrapper itself has no runtime state.

## Dependencies And Integration Points
It depends on GCE dynamic generation scripts to populate generated menus and on Terraform GCE modules consuming those symbols.

## Risks And Test Signals
Missing generated fragments can break menu rendering. GCE resource availability varies by project/zone, so stale machine/image menus can mislead users. Tests should run generator targets, menuconfig/olddefconfig, and Terraform variable generation for representative GCE configs.
