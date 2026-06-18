# sources/test-tools/kdevops/terraform/oci/scripts/publisher_definitions.yml

Purpose: YAML catalog of known OCI Linux image publishers and display-name regexes for `gen_kconfig_image`.

The schema maps publisher keys such as `oracle`, `ubuntu`, `centos`, and `fedora` to `publisher_name`, `description`, `display_name_patterns`, and `priority`. Patterns are Python regexes evaluated case-insensitively by the generator.

There is no executable control flow or dynamic state in this file. It is static input for image classification, menu ordering, and help text. The comments document update steps using `oci compute image list`, pattern selection, verification with `--publishers`, and regeneration of `Kconfig.images`.

Risks include stale patterns when OCI changes image naming, overlapping patterns where priority and dictionary order determine classification, and excluding distributions whose names lack `Linux`-style conventions until dynamic discovery catches them. Test signals should parse the YAML, enforce required keys, compile each regex, match representative image names, and verify static and dynamically discovered publishers merge without overwriting intended definitions.
