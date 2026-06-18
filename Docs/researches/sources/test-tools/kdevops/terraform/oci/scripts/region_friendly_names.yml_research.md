# sources/test-tools/kdevops/terraform/oci/scripts/region_friendly_names.yml

Purpose: YAML map from OCI region identifiers to friendly labels used in generated Kconfig menus. It contains 41 entries ordered to match Oracle documentation.

The schema is `region-identifier: "Friendly Display Name"`. `gen_kconfig_location` loads it through `load_yaml_config()` and generates fallback labels from region names when keys are missing.

There is no executable control flow. Persistence is static source content with a verification date, total-region count, ordering requirement, and update instructions. Integration is with OCI region menu generation and user-visible Kconfig labels; actual deployable values remain OCI region IDs and region keys.

Risks include stale verification metadata, new OCI regions missing from the map, order drift versus documentation, and documentation being HTML rather than a stable API. The file correctly points maintainers toward CLI/API sources for programmatic access. Test signals should parse YAML, compare comment count to actual entries, compare keys to mocked `list_regions()` output, and ensure missing friendly names fall back gracefully.
