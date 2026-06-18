# sources/test-tools/kdevops/terraform/oci/scripts/oci_common.py

Purpose: shared utility module for OCI Kconfig generator scripts. It centralizes OCI config access, client creation, YAML loading, Jinja environment setup, subscribed-region discovery, and region-key conversion.

Important APIs are `OciNotConfiguredError`, `get_default_region()`, `get_default_compartment()`, `get_subscribed_regions()`, `get_jinja2_environment()`, `load_yaml_config()`, `get_oci_config()`, `require_oci_config()`, `create_identity_client()`, `create_compute_client()`, `get_all_region_keys()`, and `get_region_kconfig_name()`.

Control flow is defensive: imports of the OCI SDK are lazy, missing config is converted to `OciNotConfiguredError` for optional generators, YAML failures return defaults, and region-key API failures fall back to generated three-letter names. Persistent state read includes `~/.oci/config` and script-local YAML files.

Integration points are all OCI generator scripts and their Jinja templates. Risks include type annotations that reference `oci.*` names while `oci` is only imported inside functions, which can fail without postponed annotation evaluation; region-key fallback can collide for similarly named regions; and broad YAML defaults can hide broken config. Tests should import the module in an environment without OCI installed, mock config parsing, verify YAML default behavior, and validate region key fallback/collision handling.
