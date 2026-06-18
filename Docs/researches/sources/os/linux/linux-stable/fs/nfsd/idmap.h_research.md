# File Research: sources/os/linux/linux-stable/fs/nfsd/idmap.h

## Summary
NFSD idmapping interface for NFSv4 names, uid/gid conversion, and owner/group XDR encoding.

## Main APIs
- `nfsd_idmap_init()` / `nfsd_idmap_shutdown()` when `CONFIG_NFSD_V4` is enabled.
- `nfsd_map_name_to_uid()` and `nfsd_map_name_to_gid()`.
- `nfsd4_encode_user()` and `nfsd4_encode_group()`.

## Behavior
When NFSDv4 is disabled, idmap init/shutdown compile to no-ops while mapping and encoding declarations remain available to users gated elsewhere.

## Risks
This header is only declarations; correctness depends on callers using the request’s namespace and idmapping policy consistently in implementation files.
