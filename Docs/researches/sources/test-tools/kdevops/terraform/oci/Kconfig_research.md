# sources/test-tools/kdevops/terraform/oci/Kconfig

Purpose: top-level OCI Terraform Kconfig entrypoint, gated by `TERRAFORM_OCI`. It composes generated and static OCI provider menus used by kdevops.

The file sources generated location, shape, and image menus from `terraform/oci/kconfigs/Kconfig.location.generated`, `Kconfig.shape.generated`, and `Kconfig.image.generated`. It also sources static storage, network, and identity menus. Comments direct users to `make cloud-config-oci` to populate current OCI resource information.

Control flow is Kconfig conditional inclusion and menu grouping. Persistent state is the generated Kconfig files and selected symbols emitted to yaml. Integration points are the OCI generator scripts in `terraform/oci/scripts`, Terraform OCI provider modules, and the broader kdevops configuration flow.

Risks include missing generated files before `make cloud-config-oci`, stale generated choices after OCI resources change, and inconsistent file naming if scripts emit `Kconfig.images` or `Kconfig.shapes` while this file expects singular generated names. Test signals should run Kconfig parsing with generated fixtures and verify provider-specific generated files are created before menu evaluation.
