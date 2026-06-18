# sources/test-tools/kdevops/terraform/oci/scripts/gen_kconfig_shape

Purpose: Python generator for OCI compute shape Kconfig. It queries shapes across subscribed or selected regions, optionally merges catalog-only shapes, groups shapes by flex/fixed/bare-metal categories, and renders Kconfig menus or raw tables.

Important functions include `get_all_shapes()`, `get_catalog_shapes()`, `merge_catalog_shapes()`, `parse_all_shape_families()`, `get_gpu_info()`, `extract_cpu_architecture()`, `extract_memory_info()`, `extract_ocpu_info()`, `extract_network_info()`, `extract_storage_info()`, `extract_shape_info()`, `get_shape_family_info()`, and rendering helpers. It depends on OCI Compute clients, compartment discovery, subscribed-region discovery, YAML loading, and Jinja templates from `oci_common`.

Control flow requires optional OCI config, determines region scope, lists shapes, merges catalog entries when requested, and then emits families, a single family, or full grouped shape menus. Catalog entries are represented by `SimpleNamespace` with minimal properties and `is_catalog_shape=True`.

State is live shape data, static catalog YAML, and stdout. Risks include duplicate shape-extraction logic diverging between `extract_shape_info()` and `get_shape_family_info()`, heuristic family parsing, minimal catalog properties producing "Flexible" placeholders, and no explicit region availability map after aggregation. Tests should cover flex option extraction, architecture heuristics, catalog merge dedupe, family parsing, and rendering of catalog markers.
