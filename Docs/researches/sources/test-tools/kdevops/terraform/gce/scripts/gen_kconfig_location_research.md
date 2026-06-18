# sources/test-tools/kdevops/terraform/gce/scripts/gen_kconfig_location

Purpose: Python generator for GCE location Kconfig. It queries Compute Engine regions and zones through helpers in `gce_common.py`, joins that live API data with `region_friendly_names.yml`, and renders `regions.j2` and `zone.j2` menus.

Important functions include `load_region_friendly_names()`, `get_region_friendly_name()`, `get_all_regions()`, `get_all_zones_by_region()`, `get_region_zones()`, `get_region_info()`, and output helpers for raw tables or Kconfig. The CLI supports full generation, `--regions`, a single region argument, `--format`, and `--quiet`.

Control flow starts by parsing arguments, requiring optional GCE credentials, then either parallel-fetches regions/zones for full Kconfig generation or fetches only region data for narrower commands. Missing GCE config exits 0 so `make dynconfig` can continue when GCE is not configured.

State is external: credentials, project, live GCE API responses, YAML friendly names, and generated stdout. Risks include stale friendly-name YAML, API schema/status drift, default region selection that may not exist, and duplicated zone queries for single-region inspection. Test signals should mock `gce_common` API helpers and validate empty-result exits, fallback friendly names, and rendered Kconfig symbols.
