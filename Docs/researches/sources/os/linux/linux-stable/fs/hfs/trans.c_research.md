# File Research: sources/os/linux/linux-stable/fs/hfs/trans.c

## Scope

Converts classic HFS names between on-disk Macintosh Pascal strings and Linux filename byte strings, with optional NLS transcoding.

## APIs And Behavior

- `hfs_mac2asc()` converts an HFS name to an output filename buffer, caps source length at `HFS_NAMELEN`, maps `/` to `:`, optionally transcodes disk NLS to Unicode then IO NLS, and returns output byte length.
- `hfs_asc2mac()` converts a Linux `qstr` to an HFS name, maps `:` to `/`, optionally transcodes through IO/disk NLS tables, caps output to `HFS_NAMELEN`, stores length, and zero-fills the remaining name buffer.

## State And Dependencies

Uses `HFS_SB(sb)->nls_disk` and `nls_io` from mount options. The converted names feed catalog key creation and readdir output.

## Risks And Invariants

The separator mapping is intentionally asymmetric for Linux legality versus HFS legality. Failed conversions substitute `?` except for output-space exhaustion, where conversion stops. Output is not NUL terminated by `hfs_mac2asc()`.
