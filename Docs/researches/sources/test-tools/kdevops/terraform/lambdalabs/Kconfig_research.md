# sources/test-tools/kdevops/terraform/lambdalabs/Kconfig

Purpose: top-level Lambda Labs Terraform Kconfig entrypoint, gated by `TERRAFORM_LAMBDALABS`. It wires provider-supported menus into kdevops configuration and documents provider limitations.

It sources `terraform/lambdalabs/kconfigs/Kconfig.location`, `Kconfig.compute`, and `Kconfig.identity` under Resource Location, Compute, and Identity & Access menus. Storage and OS menus are intentionally absent because the `elct9620/lambdalabs` Terraform provider lacks OS selection, volume management, custom user creation, and cloud-init/user-data support.

Control flow is Kconfig conditional inclusion only. State persists through selected symbols emitted to yaml by included files. Integration points are the Lambda Labs Terraform provider and kdevops-generated extra vars.

Risks include provider feature drift: if the provider gains storage or image selection, this Kconfig will hide available capabilities until updated. The comment also has a minor typo in the provider name line but not functional impact. Test signals should include Kconfig parsing, confirming menus appear only when `TERRAFORM_LAMBDALABS=y`, and verifying unsupported storage/OS symbols are not referenced by Lambda Labs Terraform templates.
