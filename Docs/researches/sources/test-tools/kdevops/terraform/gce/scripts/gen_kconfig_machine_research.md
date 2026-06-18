# sources/test-tools/kdevops/terraform/gce/scripts/gen_kconfig_machine

Purpose: Python generator for GCE machine-type Kconfig. It discovers GCE machine types by zone or aggregated all-zone API, groups them into machine series, annotates those series with curated metadata, and renders series and per-type menus.

Important data and APIs include `SERIES_METADATA`, boot-disk constants for Persistent Disk versus Hyperdisk, `extract_machine_series()`, `extract_machine_family()`, `parse_all_machine_series()`, `get_machine_series_info()`, `natural_sort_key()`, `get_all_machine_types()`, and Kconfig/raw output helpers. It relies on `gce_common` for credentials, default zone, Jinja environment, machine type symbol naming, and REST calls.

Control flow validates optional GCE credentials, chooses the default zone unless `--all-zones` is set, loads machine types, and then emits all machine choices, only series choices, or a single series. Custom machine types are intentionally filtered out.

State is mostly derived from live GCE API results plus the static metadata table. Risks include metadata lag for new series, heuristic parsing of names like GPU/local-SSD/bare-metal variants, and boot-disk type assumptions for C4/C4A/N4. Tests should cover parser edge cases, natural ordering, duplicate suppression, metadata fallback, and render variables passed to `series.j2` and `machine_type.j2`.
