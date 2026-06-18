# sources/test-tools/kdevops/terraform/azure/scripts/gen_kconfig_size

## Purpose
This script discovers Azure VM sizes and capabilities, groups them into families, and renders a hierarchical Kconfig menu for family and size selection.

## Important APIs, Types, And Functions
`get_all_vm_sizes_and_capabilities()` queries one or more regions, deduplicates size names, and filters Gen1-only sizes using `HyperVGenerations`. `extract_vm_size_family()` parses family prefixes from names like `Standard_D2s_v3`. `parse_vm_size_families()` computes per-family counts and min/max CPU/memory. `get_vm_size_family_info()` returns detailed raw records for one family. `determine_architecture()` identifies ARM64 Dp/Dpds families. `natural_sort_key()` sorts VM names numerically. `load_family_metadata()` reads `vm_family_metadata.yml`. `output_families_kconfig()` builds family metadata, per-size capability data, defaults, and renders `families.j2`. CLI parsing supports family query, `--families`, `--all-regions`, `--region`, `--format`, and `--quiet`.

## Control Flow
`main()` validates Azure credentials with optional skip, chooses either an explicit region, all regions, or the default region, fetches sizes/capabilities, then lists families, details a family, or emits Kconfig. Full Kconfig output groups sizes by family and chooses the default family containing `Standard_DS3_v2` when available.

## State And Persistence
The script writes stdout only. It reads `vm_family_metadata.yml`, Azure CLI auth/config, and live SKU metadata. In-memory state includes deduplicated sizes and capabilities keyed by size name.

## Dependencies And Integration Points
It depends on `azure_common.py`, PyYAML, Azure resource SKU APIs, and Jinja template `families.j2` or older `sizes.j2`. Generated size menus are sourced by Azure Kconfig and later consumed by Terraform variable generation.

## Risks And Test Signals
Family extraction is regex-based and may group new Azure families poorly. Filtering `HyperVGenerations == "V1"` assumes capability strings are present and exact. ARM detection only covers Dp/Dpds patterns. Loading metadata is best-effort, so missing descriptions do not fail generation. Tests should use fixture SKUs with Gen1/Gen2, ARM, accelerated networking, new-family names, default-size absent/present, all-regions deduplication, and missing metadata file.
