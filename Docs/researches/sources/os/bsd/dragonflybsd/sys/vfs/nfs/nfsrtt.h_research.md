# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsrtt.h

## Purpose

`nfsrtt.h` defines optional circular performance-monitor logs for NFS client RPC round-trip timing and NFS server response timing.

## Main Contents

- `NFSRTTLOGSIZ` sets both logs to 128 entries.
- `struct nfsrtt` stores client-side completion-order RPC timing entries:
  - procedure id, measured RTT, timeout, in-flight count, congestion window, smoothed RTT, deviation, mount fsid, timestamp.
- Server-side `DRT_*` flags identify NQNFS, TCP transport, cached reply, cached drop, and NFSv3 use.
- `struct nfsdrt` stores server-side reply-time entries:
  - flags, procedure id, client IP address, response time in microseconds, timestamp.

## Notable Details

- The log `pos` field is the next write position, so chronological traversal wraps around the circular buffer.
- Logging is controlled externally by global `nfsrtton`.
- Server log uses `INADDR_ANY` to represent non-IP clients.

## Integration

Server-side entries are written by `nfsd_rt()` in `nfs_syscalls.c`; client-side logging is used by the request/socket path outside this header.
