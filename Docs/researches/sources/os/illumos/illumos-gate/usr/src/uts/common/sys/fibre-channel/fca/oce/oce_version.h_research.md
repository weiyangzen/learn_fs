# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_version.h

This header defines the OCE driver version strings, module name, description, and identification string.

Key contents:
- Version components:
  - `OCE_MAJOR_VERSION` = `"1"`
  - `OCE_MINOR_VERSION` = `"2"`
  - `OCE_RELEASE_NUM` = `"0"`
  - `OCE_PROTO_LEVEL` = `"e"`
- Combined `OCE_VERSION` string.
- `OCE_REVISION`, `OCE_MOD_NAME`, `OCE_DESC_STRING`, and `OCE_IDENT_STRING`.

Dependencies:
- No external includes.
- Uses C++ guards.

Research notes:
- The version string is consumed by driver identity/reporting paths, including `oce_ioctl.h` query payloads and logging via `OCE_MOD_NAME`.
