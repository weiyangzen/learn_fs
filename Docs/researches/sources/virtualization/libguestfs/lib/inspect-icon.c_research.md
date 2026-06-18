# File Research: sources/virtualization/libguestfs/lib/inspect-icon.c

Purpose: Implements OS icon extraction for inspection, returning a PNG buffer or an empty buffer when no icon is found.

Key behavior:
- `guestfs_impl_inspect_get_icon` first optionally checks `/etc/favicon.png`, then falls back to distro/type-specific icon locations or Windows extraction.
- PNG candidates are validated with `is_file`, `realpath`, `file` output prefix, geometry bounds from 16x16 to 1024x1024, and max-size limits before download.
- Supports Fedora, RHEL-family, Debian, Ubuntu, Mageia, openSUSE/SLES, CirrOS, Void, ALT Linux, Gentoo, OpenMandriva, and selected Windows versions when build-time tools exist.
- CirrOS text logo is rendered through `pbmtext | pnmtopng` when tools are configured.
- Windows extraction downloads `explorer.exe` or known PNG sources and uses `wrestool`, `bmptopnm`, `pamcut`, and `pnmtopng` for XP/7/8 cases.
- `guestfs_int_download_to_tmp` is defined here as a shared inspection helper: it size-checks a guest file, creates a temp file, downloads via `/dev/fd/<fd>`, and returns the temp path.

Dependencies and state:
- Depends on inspection getters, generated file/download actions, external image tools based on configure macros, command helpers, and whole-file reads.
- Uses temporary files tied to the handle lifecycle.

Risks:
- Icon support is intentionally incomplete and depends on host tools compiled into macros.
- Windows support is version-specific and fragile around resource IDs and executable layout.
- Uses `guestfs_file` output text for PNG detection and geometry parsing.
