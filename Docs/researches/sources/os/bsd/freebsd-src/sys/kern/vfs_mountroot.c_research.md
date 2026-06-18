# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_mountroot.c

## Role

Implements root filesystem mounting during boot and reroot-style root replacement. It builds the root mount configuration, mounts temporary or persistent devfs, parses boot directives, waits for root devices, mounts candidate root filesystems, shuffles the mount list so the selected root becomes `/`, and finalizes global root state.

## Main Entry Points

- `root_mount_hold()`, `root_mount_hold_token()`, and `root_mount_rel()` let subsystems delay root mounting until devices or prerequisites are ready.
- `root_mounted()` reports completion.
- `vfs_mountroot()` is the top-level boot root mount sequence.
- Internal helpers mount devfs, parse configuration, mount candidates, read `/.mount.conf`, wait for devices, and shuffle root/devfs mounts.

## Root Hold Mechanism

Root holds are stored in a TAILQ protected by `root_holds_mtx`. Holds are visible through `vfs.root_mount_hold`. `vfs_mountroot_wait()` waits for GEOM idleness and an empty hold list, printing waiting tokens at a rate-limited cadence.

`root_mount_timeout` defaults to 3 seconds and is tunable via `vfs.mountroot.timeout`. `vfs.root_mount_always_wait` can force waiting even when the target device already exists.

## Devfs And Root Shuffle

`vfs_mountroot_devfs()` either reuses an existing `rootdevmp` or allocates/mounts a devfs mount at `/dev`, inserts it at the head of `mountlist`, sets `rootvnode`, and creates a temporary `/dev -> /` symlink.

`vfs_mountroot_shuffle()` rearranges `mountlist` so the newly mounted root is first and devfs is placed under `/dev`. It clears old mountpoint state, updates `rootvnode`, remounts the previous root under `/.mount` or `/mnt` when possible, repairs devfs coverage, purges name caches, and removes the temporary `/dev/dev` symlink when devfs was the old root.

## Configuration Parser

The parser consumes a line-oriented mountroot language. Mount entries use `fstype:device [options]`. Directives include:

- `.ask` for interactive manual root selection.
- `.md <path>` to attach a vnode-backed md device for root mounting.
- `.onfail continue|panic|reboot|retry` to set failure policy.
- `.timeout <seconds>` to change retry timeout.

`vfs_mountroot_conf0()` seeds the configuration from boot flags, `ROOTDEVNAME`, `RB_CDROM`, loader variables `vfs.root.mountfrom` and `vfs.root.mountfrom.options`, and `rootdevnames[]`, with `.ask` as a fallback when not already requested.

## Mount Attempt Flow

`parse_mount()` splits `fstype:device`, substitutes `md#` when an md unit was attached, parses optional comma-separated options, validates filesystem availability, waits for the root device when needed, builds kernel mount arguments (`fstype`, `/`, `from`, `errmsg`, `ro`, options), and calls `kernel_mount(..., MNT_ROOTFS)`. Failed attempts are retried for `root_mount_timeout` except for selected terminal errors.

`vfs_mountroot_parse()` walks the configuration until a new root mount appears after devfs in `mountlist`, then applies the configured on-failure action.

After a successful first root mount and shuffle, `vfs_mountroot()` attempts to read `/.mount.conf` from the mounted root and parse it as another configuration, allowing boot media to redirect to the final root.

## Device Waiting

`vfs_mountroot_wait_if_neccessary()` waits unconditionally for ZFS, NFS-like filesystems, p9fs, empty device strings, or forced wait mode. For ordinary device paths it first checks whether the path exists, waits for root holds and GEOM idleness, then polls until timeout.

## Finalization

`vfs_mountroot()` computes the largest mount timestamp for `inittodr()`, updates prison0's root vnode, marks `root_mount_complete` with release semantics, wakes waiters, and invokes the `mountroot` event handler.

## Dependencies

This file depends on the generic mount API in `vfs_mount.c`, filesystem lookup in `vfs_init.c`, pathname lookup, devfs, GEOM device discovery, md device ioctls, kernel file operations, jail/prison root state, name cache purge, and event handlers.

## Notes

The parser is deliberately small and boot-oriented. It tolerates invalid directives by advancing to the next line, supports interactive recovery through `.ask`, and always mounts initial root candidates read-only by ignoring `rw`/`noro` options in `parse_mountroot_options()`.
