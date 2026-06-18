# sources/user-network-fs/nfs-utils/support/nfsidmap/nfsidmap_common.c

Purpose: `nfsidmap_common.c` provides shared helpers for libnfsidmap plugins: local realm list derivation, no-strip/reformat policy parsing, and NSS buffer sizing.

Important APIs and control flow: `get_local_realms` returns cached `General/Local-Realms`; if absent it allocates a one-entry list containing the upper-case default NFSv4 domain. `free_local_realms` clears that cache. `get_nostrip` parses `General/No-Strip` into `IDTYPE_USER`/`IDTYPE_GROUP` flags and optionally sets `reformat_group` from `General/Reformat-Group`. `get_pwnam_buflen` and `get_grnam_buflen` use `sysconf` with a 16 KiB fallback.

State, dependencies, and integration: Static globals cache local realms, no-strip, and group reformat policy. It depends on `conffile.h`, `nfsidmap_private.h`, and `nfs4_get_default_domain`; plugins must initialize configuration first.

Risks and test signals: Allocation failure in the default realm path can leak the partially allocated list. Cached policy is not reset except process/plugin teardown. Tests should cover absent/present `Local-Realms`, all `No-Strip` variants, `Reformat-Group`, and sysconf fallback.
