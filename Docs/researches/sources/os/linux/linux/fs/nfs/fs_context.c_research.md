# File Research: sources/os/linux/linux/fs/nfs/fs_context.c

## Purpose
Implements NFS mount/fs_context handling for the new mount API and legacy binary mount data. It parses options, validates transport/version/security settings, prepares NFS fs contexts, and registers `nfs`/`nfs4` filesystem types.

## Mount Parameters
Defines the NFS parameter table for options such as:
- Version: `v2`, `v3`, `v4`, `vers=`, `nfsvers=`, `minorversion=`.
- Transport: `proto=`, `tcp`, `udp`, `rdma`, `xprtsec=`.
- TLS keys: `cert_serial`, `privkey_serial`.
- Cache/consistency: `ac`, `noac`, `cto`, `lookupcache`, `rdirplus`, `fsc`.
- Locking: `lock`, `local_lock`.
- Retry behavior: `soft`, `softerr`, `hard`, `softreval`, `timeo`, `retrans`, `fatal_neterrors`.
- Mount protocol options for NFSv2/v3.
- Multi-connection: `nconnect`, `max_connect`.
- Security flavors: `sec=`.

## Parsing and Validation
`nfs_fs_context_parse_param()` uses `fs_parse()` and updates `struct nfs_fs_context`. It handles booleans, numeric bounds, address parsing via `rpc_pton()`, string ownership transfer, transport tokens, security flavor lists, and sloppy option behavior.

`nfs_validate_transport_protocol()` rejects unsupported UDP cases, defaults unknown transport to TCP, and maps TCP plus `xprtsec` into `XPRT_TRANSPORT_TCP_TLS`.

`nfs_parse_source()` splits `fc->source` into hostname and export path, including bracketed IPv6 hostnames.

`nfs_fs_context_validate()` checks:
- Source presence.
- Version/minor version compatibility.
- Migration option constraints.
- Address family consistency with `proto=`/`mountproto=`.
- Server address validity.
- Transport validity.
- NFSv4 availability.
- Port defaults.
- Source parsing limits.
- NFS protocol module lookup and `fc->fs_type` correction.

## Legacy Mount Data
`nfs23_parse_monolithic()` converts old `struct nfs_mount_data` for NFSv2/v3, including legacy filehandles, flags, timeouts, lock behavior, SELinux context compatibility, and transport validation.

When NFSv4 is enabled, `nfs4_parse_monolithic()` handles `struct nfs4_mount_data`, including compat syscall conversion, user pointer copies, auth flavor, host/export/client strings, and protocol validation.

## Context Lifecycle
`nfs_init_fs_context()` allocates defaults for fresh mounts or copies current server state for reconfigure/remount. It allocates `mntfh`, sets default timeouts/cache values, selects TCP by default, initializes TLS policy fields, and attaches fs context ops.

`nfs_fs_context_dup()` deep-copies resource-owning fields where needed. `nfs_fs_context_free()` releases server refs, module refs, strings, fhandles, clone fattrs, and context memory.

## Filesystem Registration
Exports:
- `nfs_fs_type`
- `nfs4_fs_type` when NFSv4 is enabled

Both use `nfs_init_fs_context`, `nfs_fs_parameters`, and `nfs_kill_super`.

## Research Notes
This file is the main user/kernel boundary for NFS mounts. Option parsing here directly controls transport security, version selection, cache semantics, locking behavior, fallback policy, and protocol module handoff.
