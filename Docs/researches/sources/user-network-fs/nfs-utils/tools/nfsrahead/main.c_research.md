<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/main.c -->
# sources/user-network-fs/nfs-utils/tools/nfsrahead/main.c

## Purpose

`main.c` implements the `nfsrahead` udev helper. Given a bdi device number, it determines whether the device belongs to an NFS mount and prints the configured readahead value for that NFS kind so udev can write it to `read_ahead_kb`.

## Important APIs, Types, and Functions

`struct device_info` stores the device number string, `dev_t`, mountpoint, and fstype. `fill_device_number` parses `major:minor`. `get_mountinfo` uses libmount to parse mountinfo and find the mount by device number. `get_device_info` fast-rejects non-anonymous-block devices, waits up to `MNT_NM_TIMEOUT` for mountinfo changes through a libmount monitor, and falls back to short sleeps. `conf_get_readahead` reads `[nfsrahead]` config keys for the fstype or default. `main` handles `-d`/`-F`, logging, config initialization, lookup, fstype validation, and stdout output.

## Control Flow

udev invokes the helper with one bdi key. The helper initializes nfsconf and xlog, validates exactly one remaining argument, resolves that device to a mount, skips non-NFS devices, rejects non-`nfs*` filesystems, reads a configured `nfs`, `nfs4`, or default readahead value, prints the integer, frees allocations, and exits with the lookup/validation status.

## State and Persistence Behavior

The helper does not persist data. It reads `NFS_CONFFILE`, `/proc/self/mountinfo`, and mount notifications, then emits a value for udev to persist into a kernel sysfs attribute for the lifetime of that bdi.

## Dependencies and Integration Points

It depends on libmount table/monitor APIs, sysmacros `makedev`, nfs-utils xlog and conffile support, udev calling conventions, and anonymous block-device numbering for network filesystems.

## Risks and Edge Cases

`get_mountinfo` frees `device_number` on exit even though `free_device_info` later tolerates NULL. Major-number fast rejection assumes NFS bdi devices always begin with `0:`. Waiting in udev is bounded but still can delay event handling. `strtol` parsing does not validate trailing junk. Any fstype beginning with `nfs` passes, intentionally covering `nfs4` but also relying on prefix semantics.

## Test Signals

Tests should cover valid NFS and NFSv4 mountinfo fixtures, non-`0:` fast rejection, malformed device strings, delayed mountinfo appearance, missing fstype, non-NFS fstype rejection, config-specific and default readahead values, and `-d`/`-F` logging paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/main.c -->
