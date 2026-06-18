# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfallocate.8.in

## Role

Manual page for `ntfsfallocate`, a tool for preallocating space for a file or arbitrary NTFS attribute.

## Documented Interface

Documents mandatory `--length`, optional `--offset`, `--no-size-change`, `--no-action`, `--force`, quiet/verbose/version/help, and advanced attribute type/name parameters.

## Important Behavior

Warns that preallocated unwritten clusters can produce NTFS layouts unsupported by Windows, possibly causing Windows crashes when later writing those clusters. It also documents SI/decimal and IEC/binary suffix parsing for sizes.

## Research Notes

The manpage’s warning matches the source-level warning and the implementation’s direct cluster allocation behavior.
