# File Research: sources/os/linux/linux/fs/nfsd/nfs4idmap.c

This file implements NFSD NFSv4 owner/group idmapping between wire-format owner strings and kernel UID/GID values. It maintains per-network-namespace SUNRPC cache details for both ID-to-name and name-to-ID directions, performs upcalls to user space idmap handling, and provides exported mapping helpers used by NFSv4 XDR encode/decode paths.

Primary responsibilities:
- Maintain `nfs4.idtoname` cache for local numeric uid/gid plus auth domain to NFSv4 owner/group names.
- Maintain `nfs4.nametoid` cache for NFSv4 owner/group names plus auth domain to local numeric ids.
- Register/unregister per-netns idmapping cache instances.
- Encode UID/GID attributes as NFSv4 owner strings.
- Decode owner strings into kernel `kuid_t` / `kgid_t`.
- Support numeric owner strings for `AUTH_SYS` when `nfs4_disable_idmapping` is enabled.

Important entry points and exports:
- `nfsd_idmap_init()` creates and registers per-netns `idtoname_cache` and `nametoid_cache`.
- `nfsd_idmap_shutdown()` unregisters and destroys both per-netns caches.
- `nfsd_map_name_to_uid()` maps wire owner names to `kuid_t`.
- `nfsd_map_name_to_gid()` maps wire group names to `kgid_t`.
- `nfsd4_encode_user()` converts a kernel uid through the request namespace and encodes an NFSv4 owner value into XDR.
- `nfsd4_encode_group()` does the same for gid values.

Core structures and cache behavior:
- `struct ent` is the cache item: `cache_head`, type user/group, numeric id, mapped name, auth domain name, and RCU head.
- `ent_init()` copies cache item fields for insert/update.
- `ent_put()` frees entries using `kfree_rcu()`.
- `idtoname_hash()` combines auth domain, id, and user/group type.
- `nametoid_hash()` hashes the name string; matching additionally checks type and auth domain.
- Cache request format is qword-based and includes auth domain, type, and either id or name.
- Parse functions consume user-space replies, set expiry, mark negative entries for misses, and update the SUNRPC cache.

Control flow:
- A mapping helper creates a stack `struct ent` key with type, auth domain from `rqst_authname()`, and either name or id.
- `idmap_lookup()` performs cache lookup and `cache_check()`, retrying if a timeout raced with a cache replacement.
- Name-to-id maps `-ENOENT` to `nfserr_badowner`; other errors go through `nfserrno()`.
- ID-to-name falls back to numeric ASCII encoding on `-ENOENT`.
- When `nfs4_disable_idmapping` is true and the request auth flavor is below `RPC_AUTH_GSS`, name-to-id first accepts numeric strings directly and id-to-name always emits ASCII ids.

State and synchronization:
- Per-netns cache pointers live in `struct nfsd_net`.
- Cache lifetime is managed through `cache_create_net`, `cache_register_net`, `cache_unregister_net`, and `cache_destroy_net`.
- Cache entries are RCU-freed via `kfree_rcu`.
- Mapping calls rely on the SUNRPC cache and request cache handle for upcall deferral/waiting.

Dependencies and integration:
- Uses SUNRPC cache APIs and qword parsing/encoding.
- Uses `rqstp->rq_gssclient` or `rqstp->rq_client` auth domains to partition mappings by authentication context.
- Uses `nfsd_user_namespace()` to convert between kernel namespace ids and on-wire numeric ids.
- Called by NFSv4 attribute encode/decode in NFSD XDR paths.
- Warns if idmapping fails because idmapd is absent or has died.

Error handling and notable risks:
- Public mapping functions warn that `RQ_USEDEFERRAL` must be clear before idmap lookup because NFSv4 compounds must not be dropped; callers rely on compound setup to clear it.
- Name and auth strings are bounded by `IDMAP_NAMESZ`; overlong values become `nfserr_badowner` or parse failures.
- `simple_strtoul()` is used in one cache parser for id replies, while public numeric-name parsing uses `kstrtouint()`.
- Negative cache entries are valid behavior and directly affect owner resolution.
- Numeric fallback for `AUTH_SYS` is compatibility-sensitive and controlled by module parameter.
