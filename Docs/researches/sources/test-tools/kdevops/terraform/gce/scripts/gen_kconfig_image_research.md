# sources/test-tools/kdevops/terraform/gce/scripts/gen_kconfig_image

## Purpose
This executable Python script discovers GCE public Linux image families for known publishers and renders OS-image Kconfig menus or raw publisher/image tables.

## Important APIs, Types, And Functions
`get_known_publishers()` loads `publisher_definitions.yml` with fallback to Debian and CentOS. `classify_family()` converts GCE image family names into version keys and friendly labels for Debian, CentOS/Stream, Ubuntu/minimal/LTS, Red Hat, Rocky, AlmaLinux, Fedora, openSUSE, SUSE/SLES, and Oracle while preserving architecture suffixes. `organize_images_by_publisher()` queries each publisher project in parallel, filters family names through configured regexes, classifies families, and returns nested publisher/version dictionaries. `output_images_kconfig()` renders `image_distributions.j2` and `image_publisher.j2`, sorts publishers by priority and versions numerically, and notes whether ARM64 images exist. Raw output functions list publishers or versions.

## Control Flow
`main()` can list publishers without credentials. Otherwise it filters publishers if requested, validates GCE credentials with optional skip-on-absent behavior, logs the project, organizes image families, exits 1 if none are found, and emits either Kconfig or raw output. For single-publisher Kconfig mode it still renders Kconfig for that subset.

## State And Persistence
The script writes generated output to stdout only. It reads publisher YAML definitions and live GCE image project data. Runtime state is an in-memory organized image mapping.

## Dependencies And Integration Points
It imports `gce_common.py`, uses REST API helpers through `requests` sessions, and renders Jinja templates from the GCE scripts directory. Its generated file is sourced by the GCE Kconfig wrapper.

## Risks And Test Signals
Classification is naming-convention dependent and can miss new image families. Publisher YAML absence reduces coverage to a fallback list. Parallel project queries may hide per-publisher failures behind warnings. Some families lack architecture metadata and default to x86. Tests should mock image families for every classification branch, verify regex filtering, check deprecated/newer selection via `gce_common`, assert no-credential exit 0, and render templates with ARM64 and x86 variants.
