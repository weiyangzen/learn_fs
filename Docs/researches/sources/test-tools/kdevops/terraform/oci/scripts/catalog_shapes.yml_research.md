# sources/test-tools/kdevops/terraform/oci/scripts/catalog_shapes.yml

Purpose: YAML catalog of well-known OCI compute shapes that may not appear in `list_shapes()` for the current tenancy. It supports the `--include-catalog` mode in `gen_kconfig_shape`.

The schema maps shape names to `architectures`, optional `is_flex`, optional `is_bare_metal`, optional `has_gpu`, and `description`. Current entries cover DenseIO and GPU shapes including VM and bare-metal variants.

There is no executable control flow. The shape generator reads this file, fabricates minimal shape-like objects for missing catalog entries, and marks them as catalog shapes in raw output or Kconfig help. Persistence is static YAML plus comments tracking update date and total count.

Integration is intentionally advisory: catalog entries may require limits or regional availability not present in the user's tenancy. Risks include overpromising deployability, stale shape counts, and incomplete synthetic object properties such as memory/OCPU ranges. Test signals should validate schema, compare count comments to actual entries, ensure catalog merges do not override API-discovered shapes, and verify catalog-only shapes are marked distinctly.
