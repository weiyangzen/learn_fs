# sources/test-tools/kdevops/terraform/gce/scripts/region_friendly_names.yml

Purpose: YAML mapping from GCE region identifiers to human-readable labels used in generated Kconfig menus. It covers Africa, Asia Pacific, Australia, Europe, Middle East, North America, and South America entries.

The file has a simple `region: "Friendly Name"` schema. `gen_kconfig_location` reads it through `load_yaml_config()` and falls back to title-cased region identifiers when a live region is absent from this mapping.

There is no runtime control flow beyond YAML loading. Persistence is static repository content with a `Last Verified` comment and instructions for update via `gcloud compute regions list`, Google documentation, and regenerating `Kconfig.location`.

Integration is directly user-facing: labels appear in kdevops GCE region selection menus while the real GCE region IDs remain the deployable values. Risks include new regions missing from the map, renamed locations, or documentation drift. Test signals should parse the YAML, compare keys against a mocked or captured `list_regions()` result, and ensure missing keys produce readable fallback names rather than generator failures.
