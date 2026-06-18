# sources/user-network-fs/nfs-ganesha/src/include/gsh_status.h

Purpose: This header defines Ganesha's unified state/SAL status enum.

Important APIs/types/functions: `state_status_t` enumerates success and many failure classes, including allocation, LRU/hash/cache errors, FSAL errors, permissions, stale entries, locks, grace, share denied, bad handles, bad ranges, and server faults. `STATE_FSAL_ESTALE` aliases `STATE_ESTALE`.

Control flow: SAL/cache/state/upcall code returns these values to describe internal outcomes independently of raw FSAL status, allowing callers to map them to protocol replies or retry/cleanup behavior.

State and persistence: No state is stored. The enum values encode control decisions around lock blocking, grace period, stale state, and cache consistency.

Dependencies and integration points: Standalone header used by FSAL upcalls, state management, cache inode, and related layers.

Risks: Many errors overlap semantically with FSAL and NFS errors; inconsistent mapping can return wrong protocol status. Adding enum values requires auditing switch statements and stringification/mapping code.

Test signals: Verify FSAL-to-state mappings, upcall return handling, lock conflict/block/deadlock paths, grace-period behavior, stale handle handling, and switch exhaustiveness in status conversion helpers.
