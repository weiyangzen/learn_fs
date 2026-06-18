# sources/test-tools/kdevops/terraform/globals.mk

Purpose: shared Make variable definitions for Terraform support. It currently defines host OS prefix and the download coordinates for the external YAML Terraform provider plugin.

Important variables are `UNAME_PREFIX`, `YAML_PLUGIN_URL_DOWNLOAD`, `YAML_PLUGIN_NAME`, `YAML_PLUGIN_VERSION`, `YAML_PLUGIN_ARCH`, `YAML_PLUGIN_FILE`, and `YAML_PLUGIN_URL`. `UNAME_PREFIX` shells out to `uname -s` and lowercases the result, then the URL is assembled for `ashald/terraform-provider-yaml` release artifacts.

There is no branching control flow. State is Make-expanded environment plus the host OS name. Integration points are Terraform provider installation targets elsewhere in the kdevops make graph.

Risks include hardcoded `amd64`, pinned provider version `v2.0.2`, and assumptions that the release artifact naming convention matches `$(name)_$(version)-$(os)-$(arch)`. On non-amd64 systems this variable set likely points at the wrong binary. Test signals should inspect Make expansion on Linux and Darwin, verify URL construction, and ensure downstream installation rules fail clearly when the artifact is missing.
