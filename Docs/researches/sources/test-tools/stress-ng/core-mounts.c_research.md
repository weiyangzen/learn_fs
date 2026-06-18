# sources/test-tools/stress-ng/core-mounts.c

Purpose: enumerates mount points into a caller-provided array for filesystem-related stressors.

Important APIs/functions: public `stress_mount_get` and `stress_mount_free`, plus internal `stress_mount_add`.

Control flow: platform-specific `stress_mount_get` uses `getmntinfo`, `getmntent` over `/etc/mtab`, or a fallback list of `/`, `/dev`, and `/tmp`. `stress_mount_free` frees duplicated strings and clears slots.

State/persistence: allocates duplicated mount strings that callers must release. It does not modify mounts.

Dependencies/integration: mount headers selected by feature macros, `shim_strdup`, `shim_memset`, and filesystem stressors that need mount candidates.

Risks: `/etc/mtab` can be stale or absent; fallback paths may be unavailable; allocation failure silently drops entries; `max` must match the actual array size.

Test signals: getmntinfo/getmntent/fallback builds, unreadable mount table, and leak/cleanup checks for partial allocation.
