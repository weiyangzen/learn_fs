# sources/test-tools/kdevops/terraform/oci/scripts/gen_kconfig_image

Purpose: Python generator for OCI platform image Kconfig. It discovers Linux platform images across one or more OCI regions, classifies them by publisher/version/architecture, and renders Kconfig menus with region-specific OCID mappings.

Important functions include `discover_publishers_from_images()`, `get_known_publishers()`, `get_all_images()`, `is_recognized_image()`, `get_image_architecture()`, `classify_image()`, `organize_images_by_publisher()`, `get_release_notes_url()`, and `output_images_kconfig()`. It depends on `oci_common` for config, compartment, subscribed regions, Compute clients, region keys, YAML loading, and Jinja setup.

Control flow supports `--publishers`, a single publisher key, raw or Kconfig output, and `--region`. Normal generation requires OCI config, derives compartment from tenancy, loads region-key mappings, queries subscribed regions, merges static publisher definitions with dynamic Linux publisher discovery, keeps the newest release per version key, and renders distribution/publisher templates.

State is live OCI image data, user OCI config, static publisher YAML, and generated stdout. Risks include regex-based classification, architecture inference from names, release-date comparison by display-name string, no pagination handling, and HTML in generated reports if names were unsafe. Test signals should mock OCI images, publisher YAML, region key fallbacks, duplicate version replacement, and no-credentials exit behavior.
