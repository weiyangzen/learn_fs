# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ccms.h

## Purpose
Defines HAMMER2's CCMS cache-state data model and kernel API for local/thread cache-state locking.

## Key Elements
- Documents CCMS as a cache coherency management layer intended to integrate with VFS inode topology, persistent cache grants, and possible cluster/remote coherency.
- Defines `ccms_key_t`, `ccms_tid_t`, `ccms_state_t`, and `ccms_type_t`.
- Defines cache states: `CCMS_STATE_INVALID`, `CCMS_STATE_SHARED`, and `CCMS_STATE_EXCLUSIVE`.
- Defines type flags for inherited state, modified exclusive state, master/slave roles, quorum slave state, and recursion. The macro `CCMS_TYPE_QSALVE` appears misspelled relative to the comment's `QSLAVE`.
- Defines `struct ccms_cst` with a HAMMER2 spinlock, granted/inherited state and type, upgrade count, shared/exclusive count, blocked flag, and owning thread for exclusive state.
- Declares kernel APIs for CST init/uninit, blocking/nonblocking lock acquisition, temporary release/restore, upgrade/downgrade, unlock, upgraded unlock, ownership testing, and owner setting.

## Dependencies
Includes DragonFly kernel type/param/serialize/spinlock headers and uses `hammer2_spin_t` and `thread_t`.

## Behavior/Risks
- The comments describe a broader distributed cache-coherency architecture than the local implementation in `hammer2_ccms.c` currently provides.
- `count` semantics are central: positive means shared holders, negative means recursive exclusive depth, and zero means unlocked.
- Consumers must observe top-down higher-level CST locking rules described in the comments to avoid deadlocks.
