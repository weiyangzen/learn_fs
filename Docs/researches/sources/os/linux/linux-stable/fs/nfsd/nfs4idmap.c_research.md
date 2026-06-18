# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4idmap.c

Purpose: implements NFSD NFSv4 owner/group ID mapping between local numeric UID/GID values and protocol names. It provides bidirectional SunRPC cache-backed upcalls to userspace idmapd, with numeric fallback for AUTH_SYS when configured.

Key structures and state:
- `struct ent` is the common cache entry for both directions. It stores cache metadata, user/group type, numeric ID, mapped name, authentication domain name, and RCU free state.
- Two per-net cache instances are created from templates:
  - `nfs4.idtoname`: local numeric ID plus auth domain to NFSv4 owner/group name.
  - `nfs4.nametoid`: NFSv4 owner/group name plus auth domain to local numeric ID.
- Module parameter `nfs4_disable_idmapping` defaults true and disables idmapping for `sec=sys` when numeric owner strings can be used.

Major logic:
- Common cache operations allocate, initialize, update, and free `struct ent` entries via SunRPC cache infrastructure.
- `idtoname_request()` and `nametoid_request()` format pipe upcall requests to userspace with qword-escaped fields.
- `idtoname_parse()` and `nametoid_parse()` parse userspace downcalls, validate field lengths, set expiry times, support negative entries, and update cache entries.
- `nfsd_idmap_init()` creates and registers both per-net caches; shutdown unregisters and destroys them in reverse.
- `idmap_lookup()` wraps cache lookup/check behavior and retries if a timed-out item is replaced.
- `rqst_authname()` selects the GSS client auth domain when present, otherwise the normal RPC client domain.
- `idmap_name_to_id()` maps incoming owner/group strings to local IDs and returns `nfserr_badowner` for missing mappings.
- `idmap_id_to_name()` maps local IDs to protocol names and falls back to ASCII numeric strings if id-to-name mapping is absent.
- Public APIs `nfsd_map_name_to_uid()`, `nfsd_map_name_to_gid()`, `nfsd4_encode_user()`, and `nfsd4_encode_group()` bridge protocol XDR and kernel user namespace IDs.

Concurrency and lifetime:
- Cache entries are freed with `kfree_rcu()`.
- Per-net cache lifetimes are owned by `nfsd_net`.
- Name/ID mapping upcalls explicitly require `RQ_USEDEFERRAL` to be clear, because NFSv4 compounds cannot safely be dropped or deferred.

Important dependencies:
- Uses SunRPC cache APIs, qword parsing, and cache pipe upcalls.
- Uses `nfsd_user_namespace()` to translate through the server request’s user namespace.
- Uses `nfserrno()`/NFS status conversion and XDR stream encoding for owner/group attributes.

Risk/edge cases:
- Names longer than `IDMAP_NAMESZ - 1` are rejected as bad owners.
- Numeric fallback accepts only valid unsigned decimal strings that fit in a 32-bit ID.
- Empty names are invalid for incoming owner/group mapping.
- `sec=sys` behavior differs from RPCSEC_GSS because numeric strings are preferred when idmapping is disabled.
