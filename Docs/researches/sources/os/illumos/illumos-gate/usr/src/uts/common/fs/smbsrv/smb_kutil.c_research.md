# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_kutil.c

This file is a shared kernel utility layer for the SMB server. It implements string-size helpers, wildcard conversion, DOS attribute checks, ID pools, locked list/AVL containers, synchronization wrappers, time conversion, utilization accounting, thresholds, and simple hash bucket allocation.

Key responsibilities:
- Computes SMB ASCII/OEM vs UTF-16 string lengths depending on dialect and Unicode flags.
- Converts old DOS/LanMan wildcard syntax to NT wildcard syntax.
- Checks DOS search attributes against file attributes.
- Allocates 16-bit IDs with a bitmap-backed `smb_idpool_t`.
- Implements locked AVL/list containers with deferred destructor queues.
- Implements synchronized lists with wait-for-empty behavior.
- Provides `smb_rwx_t`, an rwlock plus condition variable helper.
- Converts between Unix, NT, DOS, GMT, and local SMB timestamps.
- Wraps AVL trees with ref-counted lifetime protection.
- Tracks latency and service-request queue utilization.
- Implements threshold gates for limiting concurrent command classes.
- Creates/destroys a simple power-of-two bucket hash table.

Important functions:
- `smb_idpool_constructor`, `smb_idpool_alloc`, `smb_idpool_free`, `smb_idpool_destructor`.
- `smb_lavl_*` for locked AVL operations and deferred object destruction.
- `smb_llist_*` for locked linked lists and deferred object destruction.
- `smb_slist_*` for mutex-protected lists with condition-variable wakeups.
- `smb_rwx_cvwait` drops and reacquires an rwlock while waiting on a CV.
- `smb_time_unix_to_nt`, `smb_time_nt_to_unix`, `smb_time_dos_to_unix`, `smb_time_unix_to_dos`.
- `smb_gmtime_r` and `smb_timegm` provide internal UTC conversion.
- `smb_avl_create`, `smb_avl_add`, `smb_avl_remove`, `smb_avl_lookup`, `smb_avl_iterate`, `smb_avl_release`, `smb_avl_destroy`.
- `smb_threshold_enter`, `smb_threshold_exit`, `smb_threshold_wake_all`.
- `smb_hash_create`, `smb_hash_destroy`, `smb_hash_uint64`.

Concurrency and lifetime:
- `smb_lavl` and `smb_llist` use rwlocks for tree/list access plus mutex-protected delete queues.
- Deferred destruction intentionally drops the delete-queue mutex while invoking destructors, allowing recursive posts.
- `smb_avl_t` protects tree destruction with `avl_state`, `avl_refcnt`, and `avl_cv`.
- Objects returned by `smb_avl_lookup` and `smb_avl_iterate` are held and must be released.
- `smb_slist_wait_for_empty` waits until `sl_count` reaches zero and is signaled by remove/move/exit paths.
- Queue/latency statistics use spin mutexes because they may be updated in high-frequency paths.

Filesystem relevance:
- These primitives back share storage, lock lists, request queues, and many SMB server object tables.
- Time conversion functions are used by protocol marshaling and file metadata translation.
- Attribute filtering affects directory search results.

Edge cases and risks:
- ID pool doubles until `SMB_IDPOOL_MAX_SIZE`; ID 0 and 0xffff are reserved.
- `smb_avl_iterate` terminates early if AVL sequence changes during iteration.
- `smb_time_nt_to_unix` preserves SMB sentinel values 0, -1, and -2.
- `smb_time_nt_to_unix` truncates seconds into a `uint32_t`, so very large NT times are constrained by Unix time representation here.
- Threshold wake-all sets threshold to zero, causing waiters to return `ECANCELED`.
