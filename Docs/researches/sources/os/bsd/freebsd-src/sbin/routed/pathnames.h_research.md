# File Research: sources/os/bsd/freebsd-src/sbin/routed/pathnames.h

Path constants for `routed` configuration and remote trace control.

Key responsibilities:
- Defines `_PATH_GATEWAYS` as `/etc/gateways`.
- Defines `_PATH_TRACE` as `/etc/routed.trace`.
- Includes `<paths.h>` for platform path definitions.
- Documents the security model for remotely requested trace files: requests must match the startup trace file or use the configured trace prefix.

Dependencies:
- Consumed by daemon configuration parsing, remote gateway handling, and trace command logic.

Notable risks:
- Remote trace control is intentionally enabled through a fixed `/etc` path; safety depends on trace implementation checks and filesystem permissions.
