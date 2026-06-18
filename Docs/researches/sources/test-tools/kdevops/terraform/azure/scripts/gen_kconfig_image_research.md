# sources/test-tools/kdevops/terraform/azure/scripts/gen_kconfig_image

## Purpose
This executable Python script discovers Azure Linux VM image offers/SKUs for known publishers and renders image-selection Kconfig or raw publisher/image tables.

## Important APIs, Types, And Functions
`load_yaml_config()` loads YAML from the script directory. `get_known_publishers()` reads `publisher_definitions.yml` with fallback to Debian/Red Hat. `score_sku_quality()` prefers Gen2 and LVM variants while avoiding CI/legacy variants. `supports_cloud_init()` filters Oracle/RHEL versions older than 7.7. `classify_offer_sku()` maps publisher offer/SKU names into version keys, friendly names, architectures, offers, and SKUs across Debian, RHEL, Oracle, Ubuntu, openSUSE, SLE Micro, SLES/SLE-HPC, and generic patterns. `organize_images_by_publisher()` queries Azure offers/SKUs and selects the best SKU per version. `output_images_kconfig()` renders `image_distributions.j2` and `image_publisher.j2`.

## Control Flow
`main()` can list publishers without credentials. Otherwise it validates Azure credentials, optionally filters to one publisher, chooses a region, organizes images, and emits raw or Kconfig output. Single-publisher Kconfig output is intentionally rejected; raw output is supported for inspection. Full Kconfig output sorts publishers by priority and versions numerically.

## State And Persistence
The script writes only stdout. It reads static publisher definitions and live Azure image metadata. In-memory state is a nested publisher/version mapping; `_score` is retained internally for selection but not intended as user-facing output.

## Dependencies And Integration Points
It imports `azure_common.py`, requires PyYAML for configured publisher definitions, uses Azure Compute image APIs through shared helpers, and renders Jinja templates. Generated output feeds `terraform/azure/Kconfig` image menus.

## Risks And Test Signals
Classification is heavily regex-based and provider naming changes can silently hide images. Marketplace publisher IDs for AlmaLinux/Rocky can change. The script assumes cloud-init requirements based on version heuristics. Missing PyYAML falls back to a minimal publisher list, which can reduce coverage without failing. Tests should use fixture offer/SKU maps for every publisher path, validate best-SKU scoring, ensure unsupported old Oracle/RHEL versions are filtered, cover missing YAML, and assert no-credential exit 0.
