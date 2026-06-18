# sources/sync-backup/rsync/usage.c

Purpose: central version, capability, algorithm-list, and usage/help output for normal and daemon rsync modes.

Important APIs/functions: `print_info_flags()` emits capabilities/optimizations as human text or JSON. `output_nno_list()` prints checksum/compression/auth algorithm lists. `print_rsync_version()` emits program/version/protocol/copyright/url/capabilities/lists/license/warranty, using JSON when passed `FNONE`. `usage()` prints command forms and includes generated `help-rsync.h`; `daemon_usage()` includes `help-rsyncd.h`. `rsync_version()` selects `RSYNC_GITVER` or `RSYNC_VERSION` and strips a leading `v`; `default_cvsignore()` returns the generated ignore pattern string.

Control flow and state: most behavior is compile-time conditional. JSON generation reuses the same capability table but converts labels into keys and booleans/bit counts. `istring()` dynamically formats bit widths; several generated strings are intentionally process-lifetime allocations.

Dependencies and integration: depends on version headers, generated help/default-ignore headers, checksum/compression registries, and `rprintf()`. Risks include JSON formatting drift, capability labels not matching compile-time behavior, and generated header availability. Test signals include `--version`, `--version --json`, help-output smoke tests, and build-feature wrappers such as the SIMD checksum test.
