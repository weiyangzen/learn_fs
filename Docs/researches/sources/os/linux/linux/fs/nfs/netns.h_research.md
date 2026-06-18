# File Research: sources/os/linux/linux/fs/nfs/netns.h

## Purpose
Defines NFS-private per-network-namespace state accessed through `net_generic()`.

## Main Data
- DNS resolver cache and block-layout device pipe/reply state.
- Per-net NFS client and volume lists.
- NFSv4-only callback identifier IDR, callback ports, callback user counts, and v4 data server cache/list lock.
- Shared NFS client pointer, client-list spinlock, boot time, RPC stats, and optional procfs directory.

## Research Notes
This is a state container header. It is central to isolating NFS client lists, callback state, and proc/stat state per network namespace.
