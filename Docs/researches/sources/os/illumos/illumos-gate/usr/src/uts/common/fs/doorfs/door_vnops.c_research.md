# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/doorfs/door_vnops.c

## Purpose
Defines vnode operations for synthetic door vnodes. These operations make door descriptors behave like VFS objects while delegating most door behavior to `door_sys.c`.

## Vnode Operations
`door_vnodeops_template` provides:
- `OPEN`: `door_open`
- `CLOSE`: `door_close`
- `GETATTR`: `door_getattr`
- `ACCESS`: `door_access`
- `INACTIVE`: `door_inactive`
- `REALVP`: `door_realvp`
- Unsupported/error operations for lock, poll, pathconf, dispose, secattr, and share locks.

## Key Functions
`door_open()`:
- Enforces labeled-system MAC policy.
- Allows cross-zone clients only when the server is in the global zone; otherwise client and server zones must match.
- Ignores invalid doors by returning success, preserving legacy open behavior.

`door_close()`:
- Handles unref notification scheduling when this is the last file-structure reference and vnode count indicates no other files reference it.
- If the door has active invocations, sets `DOOR_DELAY`; otherwise calls `door_deliver_unref()`.
- Asserts process-exit cleanup revoked current-process doors before `closeall()`.

`door_getattr()`:
- Fills synthetic attributes: type from vnode, mode `0777`, uid/gid `0`, size `0`, zero timestamps, `doordev` fsid/rdev, and nlink from vnode refcount.

`door_inactive()`:
- Defers freeing while private bound server threads remain.
- If still listed on a target process, removes the door under `door_knob`.
- Invalidates and frees vnode and `door_node_t`.

`door_bind_thread()` / `door_unbind_thread()`:
- Track private-server bindings with `door_bound_threads` under `v_lock`, without changing vnode refcount.
- `door_unbind_thread()` triggers inactive processing when the last bound thread releases an otherwise unreferenced vnode.

`door_access()`:
- Grants all access.

`door_realvp()`:
- Returns the door vnode itself.

## Integration Points
- Shares `door_knob` with `door_sys.c`.
- Calls `door_deliver_unref()` and `door_list_delete()` implemented in the syscall layer.
- Uses `VTOD()`/`DTOV()` door vnode/node conversions.
- Exports `door_bind_thread()` and `door_unbind_thread()` for private door binding.

## Risks and Subtle Areas
- `door_bound_threads` deliberately does not use `VN_HOLD()`; inactive logic must cooperate with this separate count.
- `door_close()` unref delivery depends on `count == 2` and `vp->v_count == 1`, which is tied to file/vnode lifetime semantics.
- Zone check dereferences `door_target` only after validating the door under `door_knob`.

## Testing/Validation Signals
- Open a door across zones on labeled systems.
- Close last refs with `DOOR_UNREF` while no invocations are active.
- Close last refs while invocations are active and verify delayed unref.
- Bind/unbind private server threads and verify inactive cleanup occurs only after final unbind.
