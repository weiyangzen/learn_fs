# File Research: sources/os/linux/linux-stable/fs/nfs/fs_context.c

## Purpose

Implements NFS mount context parsing and validation for the modern fs_context API, including text mount options, legacy binary NFSv2/v3/v4 mount data, remount context duplication, and `nfs`/`nfs4` filesystem type registration.

## Main Entry Points

- `nfs_fs_context_parse_param()`: parses individual text mount options.
- `nfs_parse_security_flavors()` / `nfs_parse_xprtsec_policy()` / `nfs_parse_version_string()`: parse security, transport security, and NFS version options.
- `nfs23_parse_monolithic()` / `nfs4_parse_monolithic()`: translate legacy binary mount data into `struct nfs_fs_context`.
- `nfs_fs_context_validate()`: validates addresses, versions, transports, migration use, source syntax, and loads the protocol module.
- `nfs_get_tree()`: validates and invokes the version-specific tree creation path.
- `nfs_fs_context_dup()` / `nfs_fs_context_free()`: clone and clean mount contexts.
- `nfs_init_fs_context()`: allocate defaults for new mounts or copy state for remounts.
- `nfs_fs_type` / `nfs4_fs_type`: exported filesystem type definitions.

## Control Flow And State

The parser maps a large option table into `nfs_fs_context` fields: cache behavior, close-to-open, hard/soft behavior, transports, mount side-protocol options, readdirplus policy, fscache uniquifiers, security flavors, TLS key serials, lookup caching, local locks, connection counts, and attribute timeouts. Validation checks protocol/address-family consistency, rejects UDP for NFSv4 or disabled UDP builds, maps xprtsec to TCP-TLS transports, assigns default ports, parses `host:path`, and switches `fc->fs_type` to the loaded NFS subversion module.

Legacy monolithic parsing supports old NFSv2/v3 mount structures, SELinux context passthrough for version 6 data, and NFSv4 version-1 binary mount data including compat conversion. Remount contexts are initialized from the live `nfs_server`, including network namespace and protocol module references.

## Dependencies

Depends on Linux fs_context/fs_parser, NFS mount structures, RPC transport identifiers, RPC-with-TLS handshake policy, key lookup when TLS keys are enabled, NFS protocol module lookup, and version-specific `try_get_tree()` implementations.

## Risks

Mount option interactions are subtle: version/minorversion, proto/address-family, mountproto/mountaddr, xprtsec transport support, fscache string ownership, and remount defaults must be kept consistent. Legacy binary parsing handles user pointers and historical structure versions, so bounds and compatibility checks are security-sensitive.
