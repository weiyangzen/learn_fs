## sources/user-network-fs/nfs-utils/utils/nfsidmap/nfsidmap.c

Purpose: Userspace NFSv4 id-mapping helper that resolves `name@domain` to uid/gid and uid/gid to names, then instantiates Linux keyring entries for kernel upcalls.

Important APIs/types/functions: Key operations include `keyring_clear`, `list_keyring`, `id_lookup`, `name_lookup`, and `key_invalidate`. It uses `nfs4_init_name_mapping`, owner/id conversion APIs from `libnfsidmap`, `keyctl_instantiate`, `keyctl_set_timeout`, and `/proc/keys` scanning fallback helpers.

Control flow: `main` parses clear/list/display/invalidate/upcall modes, requires root, initializes idmap config, then either handles admin actions or parses key/description pairs from request-key. Descriptions are split into type/value and dispatched to uid, gid, user, or group lookup.

State and persistence: Uses the `.id_resolver` keyring as cache, `/etc/idmapd.conf` for mapping rules, and `/proc/keys` for discovery/invalidation. On full keyring errors it clears the resolver ring and retries.

Dependencies and integration: Integrates with Linux keyutils, request-key, nfs-utils logging/config helpers, and libnfsidmap.

Risks and test signals: Risks include root-only operation, parsing `/proc/keys`, `atoi` for ids, keyring quota races, and silent unknown description types. Tests should cover all mapping directions, expired keys, invalidation masks, keyring-full retry, non-root rejection, and malformed descriptions.
