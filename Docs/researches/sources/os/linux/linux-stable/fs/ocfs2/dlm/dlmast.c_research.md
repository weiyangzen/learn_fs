# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmast.c

## Summary
Implements OCFS2 DLM AST and BAST queueing and delivery for local and remote locks. It updates lock value blocks, queues AST/BAST callbacks, cancels obsolete BASTs, handles incoming proxy AST messages, and sends proxy AST/BAST messages over the O2CB TCP transport.

## Main Responsibilities
- Queue ASTs and BASTs on `dlm->pending_asts` and `dlm->pending_basts`.
- Cancel pending BASTs that are made obsolete by a newly granted lock level.
- Update or fetch lock value blocks when ASTs are delivered.
- Invoke local AST and BAST callbacks.
- Convert remote AST/BAST delivery into `DLM_PROXY_AST_MSG` messages.
- Handle incoming proxy AST/BAST messages from remote masters.
- Move locks to granted state and update lock modes/status on remote AST receipt.

## Key Interfaces
- `__dlm_queue_ast()` and `dlm_queue_ast()` add locks to the pending AST list.
- `__dlm_queue_bast()` adds locks to the pending BAST list.
- `dlm_do_local_ast()` and `dlm_do_local_bast()` invoke local callbacks.
- `dlm_do_remote_ast()` sends a proxy AST to the lock's owning node.
- `dlm_proxy_ast_handler()` processes incoming DLM proxy AST network messages.
- `dlm_send_proxy_ast_msg()` sends proxy AST/BAST messages; `dlmcommon.h` wraps it as `dlm_send_proxy_ast()` and `dlm_send_proxy_bast()`.

## Important Behavior
BAST cancellation prevents stale blocking notifications. If an AST grants a lock down to NL, or grants PR when the highest blocked mode is not EX, a queued BAST no longer describes a real blocking condition and is removed. The code also releases the reserved AST accounting for the canceled BAST.

`dlm_update_lvb()` only updates value blocks when this node masters the lock resource. GET requests copy the lock resource LVB into the lock status block before AST callback. PUT requests are deliberately not applied here; comments state they should happen at downconvert time to avoid racing GETs and PUTs.

Incoming proxy AST handling validates domain liveness, lock name length, LVB flag combinations, AST type, lock-resource existence, and recovery/migration state. For ASTs, it searches converting first, then blocked; for BASTs, it searches converting first, then granted. A matching AST moves the lock to the granted list, applies `convert_type` to `type`, clears conversion state, sets lksb status to `DLM_NORMAL`, copies LVB data when requested, then invokes the local AST.

Unknown locks in a proxy AST are usually treated as `DLM_NORMAL` rather than fatal after logging, while recovery or migration states return `DLM_RECOVERING` or `DLM_MIGRATING`. Sending code treats those two statuses as impossible for a successful AST target and calls `BUG()`.

## State and Synchronization
AST/BAST queues are protected by `dlm->ast_lock`; individual pending bits and list links are updated under each lock's `spinlock`. Lock-resource list searches and state checks use `res->spinlock`. Lock references are taken when adding to pending lists and released if list insertion is canceled. Domain references are acquired with `dlm_grab()` while handling network messages.

## Cross-File Interactions
This file uses `o2net_send_message_vec()` from the cluster TCP layer and the DLM wire structures from `dlmcommon.h`. The DLM thread consumes pending AST/BAST lists. Lock, convert, unlock, recovery, and migration code set lock states that determine whether these callbacks are queued or accepted.

## Risks
The AST/BAST paths run at the boundary between distributed state changes and local callbacks. List placement, pending bits, and lock references must stay consistent or callbacks can be lost, duplicated, or use freed locks. LVB propagation has explicit ordering constraints. Remote AST handling trusts wire fields after validation, so name length, type, and flag checks are important. The use of `BUG()` for unexpected recovery/migration replies makes protocol-state mismatches fatal.
