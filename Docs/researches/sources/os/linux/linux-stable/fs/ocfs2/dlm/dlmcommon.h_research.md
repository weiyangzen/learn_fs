# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmcommon.h

## Summary
Defines the internal OCFS2 DLM data model, wire message formats, state flags, helper macros, inline functions, and cross-file prototypes. It is the common contract among DLM domain management, mastership, locking, conversion, unlock, AST delivery, recovery, migration, debug, and network handler files.

## Main Responsibilities
- Define lock-name limits, hash sizing, hash helpers, and owner constants.
- Define master-list entry types and `struct dlm_master_list_entry`.
- Define AST types and valid lock flags.
- Define DLM context, recovery context, work item, lock resource, migratable lock, and lock structures.
- Define lock-resource state flags and recovery state flags.
- Define all DLM network message numbers and wire packet layouts.
- Define migratable lock-resource sizing to fit O2NET one-page payloads.
- Declare internal DLM helper and network-handler functions implemented across DLM source files.
- Provide inline helpers for lock compatibility, lock-resource state mapping, node iteration, cookie decoding, and ownership updates.

## Key Interfaces
- Core state structures: `dlm_ctxt`, `dlm_lock_resource`, `dlm_lock`, `dlm_recovery_ctxt`, and `dlm_master_list_entry`.
- Wire structs: create/convert/unlock/proxy AST, master/assert/migrate/requery, join/cancel/exit, recovery, region/nodeinfo, deref, and migratable lock-resource packets.
- Handler prototypes: `dlm_create_lock_handler()`, `dlm_convert_lock_handler()`, `dlm_proxy_ast_handler()`, `dlm_unlock_lock_handler()`, mastership handlers, migration handlers, recovery handlers, and domain join/exit handlers.
- Lock-resource helpers: lookup, allocation, reference, hash insertion/removal, dirtying, purge, migration, refmap, and inflight refs.
- AST helpers: queue, local delivery, remote delivery, and proxy send wrappers.

## Important Behavior
`dlm_ctxt` is the DLM domain object. It owns lock-resource and master hash tables, dirty/purge/pending AST lists, live/domain/recovery bitmaps, recovery context, debugfs root, domain reference/state fields, worker and recovery threads, workqueue/list state, eviction callbacks, and filesystem/DLM protocol versions.

`dlm_lock_resource` is the master object for one lock name. It carries granted, converting, and blocked lists in a fixed order, purge/dirty/recovering/tracking links, owner, state flags, LVB, inflight counts, AST reservation count, waitqueue, and node refmap. Comments warn that field layout changes must respect initialization code in other files.

`dlm_lock` stores the migratable wire lock state plus local list links, AST/BAST list links, resource pointer, spinlock, reference count, callback pointers, callback data, lock status block, and pending flags for AST, BAST, convert, lock, cancel, unlock, and kernel-allocated LKSB.

Message payload sizing is tied to the transport: `DLM_MAX_MIGRATABLE_LOCKS` is chosen so one `dlm_migratable_lockres` plus 240 locks plus reserved padding fits within `O2NET_MAX_PAYLOAD_BYTES`. This is central to efficient recovery/migration of lock resources.

Lock compatibility is intentionally simple: NL is compatible with all, EX conflicts with every non-NL lock, and PR is compatible only with PR or NL. `__dlm_lockres_state_to_status()` maps recovery/migration/in-progress flags to retry statuses while holding `res->spinlock`.

## State and Synchronization
The structures embed the synchronization used throughout the DLM: domain `spinlock`, `ast_lock`, `track_lock`, `master_lock`, work locks, lock-resource `spinlock`, waitqueues for join/thread/recovery/AST/migration/resource waits, krefs for domains, locks, lock resources, and MLEs, atomic counters for statistics and AST reservations, and bitmaps for node membership and responses.

## Cross-File Interactions
Every DLM implementation file depends on this header. `dlmast.c` uses AST types, proxy AST wire structures, lock-resource/lock fields, and send wrapper declarations. `tcp.h` supplies `O2NET_MAX_PAYLOAD_BYTES` and `struct o2net_msg` used by network handlers. `dlmapi.h` supplies public status, modes, flags, LVB size, callback types, and lock status blocks.

## Risks
This header is a dense internal ABI. Wire structure layout, message ids, lock mode/status values, and migratable payload sizing must remain consistent across all nodes in a cluster. Many inline helpers assume callers hold specific spinlocks. The same structures participate in normal locking, migration, recovery, purge, AST delivery, and network handler paths; incorrect state flag transitions can make callers return `DLM_FORWARD`, `DLM_RECOVERING`, or `DLM_MIGRATING` at the wrong time. Changing payload sizes without considering `O2NET_MAX_PAYLOAD_BYTES` can break recovery message framing.
