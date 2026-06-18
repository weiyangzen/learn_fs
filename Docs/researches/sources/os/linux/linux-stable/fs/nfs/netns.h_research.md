# File Research: sources/os/linux/linux-stable/fs/nfs/netns.h

## Purpose
Defines NFS private per-network-namespace state accessed through `net_generic()`.

## Main Types
- `struct bl_dev_msg`
  - Stores block-layout device reply status and major/minor numbers.
- `struct nfs_net`
  - DNS resolver cache pointer.
  - Block layout device pipe/reply/waitqueue/mutex.
  - Per-net NFS client and volume lists.
  - NFSv4 callback ID allocator and callback port state when v4 is enabled.
  - NFSv4 data server cache and lock when v4 is enabled.
  - Per-net `nfs_netns_client`.
  - Global NFS client lock for the namespace.
  - Namespace boot time and RPC stats.
  - Optional procfs root entry.

## Exports
- Declares `extern unsigned int nfs_net_id`, the netns generic ID used by NFS code.

## Research Notes
This header is shared by client creation, NFSv4 callback/trunking code, procfs/sysfs integration, and pNFS block/data-server paths.
