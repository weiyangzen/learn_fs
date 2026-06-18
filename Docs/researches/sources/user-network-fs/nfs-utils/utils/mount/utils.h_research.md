<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/utils.h -->
# sources/user-network-fs/nfs-utils/utils/mount/utils.h

## Purpose

`utils.h` declares the shared mount/umount helper API.

## Important APIs, types, and functions

It includes `parse_opt.h` and declares `discover_nfs_mount_data_version`, `print_one`, usage printers, `chk_mountpoint`, and `nfs_umount23`.

## Control flow

No executable flow exists. The declarations support the command-line frontends and unmount path.

## State and persistence behavior

The header exposes functions that operate on process globals and parsed options, but contains no state itself.

## Dependencies and integration points

By including `parse_opt.h`, it makes the option-list type available to users of the utility helpers. It is part of the internal mount utility interface rather than a public library ABI.

## Risks and edge cases

The prototypes use mutable `char *` for some output strings, so callers must follow the implementation's ownership expectations. Header-level coupling to `parse_opt.h` can force rebuilds when the option API changes.

## Test signals

Compile tests should cover inclusion from both mount and umount translation units. ABI checks should ensure return-code conventions remain consistent with callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/utils.h -->
