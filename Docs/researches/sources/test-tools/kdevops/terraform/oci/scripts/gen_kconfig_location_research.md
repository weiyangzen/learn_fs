# sources/test-tools/kdevops/terraform/oci/scripts/gen_kconfig_location

Purpose: Python generator for OCI location Kconfig. It lists OCI regions, subscription status, home region, and availability domains, then renders region and AD selection menus.

Key functions include `load_region_friendly_names()`, `get_region_code()`, `get_region_friendly_name()`, `get_all_regions()`, `get_region_info()`, output helpers for region/raw/full Kconfig, and `parse_arguments()`. It uses OCI Identity clients and helpers from `oci_common` for default region, Jinja, config loading, and credential checks.

Control flow allows `--regions`, a specific region, `--include-unsubscribed`, raw output, or full Kconfig. Full output filters to subscribed regions by default because AD queries and deployments are not valid for unsubscribed regions. It appends a `TERRAFORM_OCI_COMPARTMENT_NAME` string config after region/AD menus.

State comes from `~/.oci/config`, tenancy region subscriptions, region list API, AD API, and static friendly-name YAML. Missing OCI config exits 0 for optional dynconfig. Risks include default region absent from filtered region list, fallback AD for unsubscribed regions being deployability-confusing, no pagination assumptions, and API errors returning partial data. Tests should mock Identity clients for subscribed/unsubscribed/home regions and AD sorting.
