# File Research: sources/virtualization/libguestfs/lib/qemu.c

QEMU feature/version helpers and drive-source formatting.

Important behavior:
- `generic_qmp_test` runs qemu with QMP on stdio, sends capabilities, a query command, and quit, then captures the query response.
- `guestfs_int_platform_has_kvm` uses QMP `query-kvm` JSON to determine whether KVM is enabled.
- JSON parsing is strict and UTF-8 validated.
- `guestfs_int_qemu_escape_param` doubles commas for qemu parameter escaping.
- `guestfs_int_drive_source_qemu_param` formats file, ftp/ftps/http/https, iscsi, nbd, rbd, and ssh sources for qemu/qemu-img.
- File paths are resolved with `realpath` so overlays reference absolute backing paths.
- RBD formatting builds escaped monitor host lists and includes auth/key options when present.
- `guestfs_int_discard_possible` validates discard support by overlay state, known source format, and protocol.

Filesystem relevance:
- Converts libguestfs drive sources into qemu-compatible backing strings and validates discard semantics for block/filesystem image operations.
