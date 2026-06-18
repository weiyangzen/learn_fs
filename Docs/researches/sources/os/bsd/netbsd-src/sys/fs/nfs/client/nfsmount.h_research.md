# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfsmount.h

## Purpose
Defines the client-side `struct nfsmount`, the per-mount state object for NFS client mounts.

## Main Data
- Embeds `struct nfsmount_common nm_com`, sharing mount lock, flags, state, timeout, hostname, and callback hooks with common NFS/NLM code.
- Stores root file handle, socket/RPC transport state (`struct nfssockreq`), timeout counters, negotiated read/write/readdir sizes, readahead, commit size, attr-cache lifetimes, write verifier, async buffer queue state, and max file size.
- Tracks namecache lifetimes with `nm_nametimeo` and `nm_negnametimeo`.
- Adds NFSv4/newnfs state: session list, client pointer, mount/system UID, client-id discriminator, fsid, minor version, Kerberos principal lengths, server principal length, and variable-length name storage.

## Main Macros
- `VFSTONFS(mp)` converts a mount to its NFS mount state.
- `NFSMNT_MDSSESSION(m)` returns the metadata-server session, assumed to be the first session.
- `NFSMNT_DIRPATH(m)` and `NFSMNT_SRVKRBNAME(m)` slice variable-length name storage.
- Field aliases expose common and socket fields as direct `nm_*` names.

## Integration
Consumed by vnode operations, RPC connection setup, NFSv4 session/state management, pNFS paths, and mount option handling.

## Risks
- Variable-length `nm_name[1]` storage depends on allocation sizing and offset macros; incorrect length accounting can corrupt principal/path strings.
- `NFSMNT_MDSSESSION` assumes the session queue is non-empty and ordered.
