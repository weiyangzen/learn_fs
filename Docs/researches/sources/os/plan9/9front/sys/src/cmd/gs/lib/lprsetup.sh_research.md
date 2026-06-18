# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/lprsetup.sh

BSD lpr print-filter setup helper for Ghostscript printers.

Main behavior:
- Defines device variants, filter names, printer device/type, Ghostscript library/filter directories, spool directory, filter script name, and printcap output filename.
- Requires `$GSDIR` to be writable.
- Creates `$GSFILTERDIR`, `direct` and `indirect` symlinks, `gs<filter>` symlinks to `../unix-lpr.sh`, and device symlink directories.
- Generates `printcap.insert` in the current directory with sample printcap entries for direct queues and dual raw-output queues.
- Prints a reminder listing spool directories that the administrator must create and initialize.

Implementation details:
- Device names may include `.dq` for dual-queue setup; base names are derived by stripping numeric suffixes.
- Serial printer entries add baud/control/mode fields.
- Only `if` is enabled by default; other filter types are present in comments or filter-generation loops.

Filesystem relevance:
- Administrative setup script that creates directories/symlinks and writes a sample printcap fragment. It is printer configuration, not filesystem implementation.
