# File Research: sources/local-fs/xfsdump/common/global.c

## Summary
Builds, frees, checksums, and validates version numbers for the xfsdump global media-file header. During dump builds it creates the dump session identity; during restore builds it can parse a requested session UUID.

## Main Responsibilities
- Allocate and initialize `global_hdr_t`.
- Fill global magic, version, timestamp, host id, dump UUID, hostname, and dump label.
- Parse relevant command-line options for dump label, dump time, format compatibility, and restore session id.
- Optionally prompt interactively for a dump label.
- Compute and verify the 32-bit additive-inverse header checksum.
- Accept known global header versions.

## Important Behavior
`global_hdr_alloc()` sets `GLOBAL_HDR_VERSION` by default. Dump builds generate a new UUID; restore builds clear it unless `GETOPT_SESSIONID` provides one.

`GETOPT_DUMPTIME` uses a specified file’s `st_mtime` as the dump timestamp. `GETOPT_FMT2COMPAT` downgrades the global header version to version 2 for compatibility.

If no dump label is supplied and dialogs are allowed, `prompt_label()` displays an interactive dialog with a timeout. If still empty, the label is stored as an empty string.

`global_hdr_checksum_set()` zeroes `gh_checksum`, sums the full header as converted 32-bit words, and writes the two’s-complement additive inverse. `global_hdr_checksum_check()` succeeds when the converted 32-bit sum of the whole header is zero.

`global_version_check()` accepts versions 0 through 3.

## Dependencies
Depends on command-line option definitions, logging/dialog helpers, UUID APIs, hostname/hostid/time/stat calls, `strncpyterm`, and `ARCH_CONVERT` integer helpers.

## Risks
`global_hdr_alloc()` returns `NULL` on several validation errors after allocating `ghdrp`, without freeing that allocation.

The checksum is over the entire fixed-size global header and assumes 32-bit word alignment and stable serialized conversion behavior.

Dump label and restore session parsing reuse global `getopt` state by resetting `optind`; this requires callers to tolerate repeated option scans.
