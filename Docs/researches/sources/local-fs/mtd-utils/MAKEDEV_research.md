# File Research: sources/local-fs/mtd-utils/MAKEDEV

## Purpose
Shell helper for creating legacy MTD, FTL, NFTL, RFD, and INFTL device nodes under `/dev`.

## Key Elements
Defines `mkftl`, `mknftl`, `mkrfd`, and `mkinftl`, each creating one base block device and 15 partition nodes. Iterates letters `a` through `p`, allocating minors in groups of 16, then creates `/dev/mtdN`, `/dev/mtdrN`, and `/dev/mtdblockN` for `0..16`.

## Dependencies
Requires bash plus privileged `mknod`, `seq`, and `expr`. Encodes historical major numbers: FTL 44, NFTL 93, RFD 256, INFTL 96, MTD char 90, MTD block 31.

## Risks
Hard-codes `/dev` paths and old static device numbering, so it is unsafe on systems managed by `udev`/`devtmpfs` and must be run with root privileges.
