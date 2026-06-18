# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/lprsetup.sh

BSD print-filter setup utility for Ghostscript.

Behavior:

- Defines printer devices, filter names, printer port/type, Ghostscript library/filter directories, spool directory, and helper names.
- Requires the Ghostscript library directory to be writable.
- Creates a filter directory, `direct` and `indirect` symlink aliases, symlinks each lpr filter name to `unix-lpr.sh`, and creates device symlinks.
- Generates a `printcap.insert` file in the current directory with example queue entries for each configured Ghostscript device.
- Handles `.dq` device suffixes as dual-queue setups with raw output queues.
- Emits a sorted reminder of spool directories/log/accounting files the administrator must create.

This is installation/admin scaffolding for Unix BSD `lpr`; it does not configure Plan 9 printing or filesystem internals.
