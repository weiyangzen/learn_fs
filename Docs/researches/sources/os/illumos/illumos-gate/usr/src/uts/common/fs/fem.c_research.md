# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fem.c

## Purpose
Implements FEM/FSEM, the illumos vnode and VFS operation interposition framework. It lets kernel components install monitor operation vectors on individual vnodes or VFS instances, so operations pass through a stack of monitors before reaching the original filesystem operations.

## Main Responsibilities
- Define vnode monitor (`fem_t`) and VFS monitor (`fsem_t`) operation vector layouts.
- Build head operation vectors that intercept every vnode/VFS op.
- Provide `vnext_*()` and `vfsnext_*()` APIs for monitors to call the next operation below them.
- Manage per-object monitor stacks with copy-on-update semantics and refcounts.
- Install, uninstall, query, and replace base vnode/VFS operations under interposition.
- Initialize guard vectors that panic on stack corruption/underrun.

## Core Structures and Concepts
- `fem_type_info`: per-type head node, guard node, and error function.
- `fem_head`: per-vnode/per-vfs object containing a mutex and current `fem_list`.
- `fem_list`: refcounted stack of `fem_node` entries.
- `fem_node`: either base ops (`fn_available == NULL`) or a monitor with ops plus opaque `fn_available` argument and optional hold/release callbacks.
- Stack bottom is a guard node; above it is the original base ops; monitors are pushed above that.
- `FEM_HEAD(FEMTYPE_VNODE)` and `FEM_HEAD(FEMTYPE_VFS)` are the installed head ops that intercept object calls.

## Operation Vector Definitions
`fem_opdef` maps all vnode operation names to offsets in `fem_t`.
`fsem_opdef` maps VFS operation names to offsets in `fsem_t`.

Guard ops:
- `fem_guard_ops` routes all vnode monitor calls to `fem_err()`.
- `fsem_guard_ops` routes all VFS monitor calls to `fsem_err()`.

Both panic if reached, indicating stack corruption.

## Dispatch Machinery
`vsop_find()` and `vfsop_find()` walk downward from a current stack node:
- If a base node is reached, select the original vnode/VFS operation and pass the base object.
- If a monitor node has the requested method, select it and pass the fem/fsem argument handle.
- Otherwise continue down.

Debug builds route through `_op_find()` using explicit offsets.

## Head Operations
`vhead_*()` functions cover the full vnode op surface: open, close, read, write, ioctl, setfl, getattr, setattr, access, lookup, create, remove, link, rename, mkdir, rmdir, readdir, symlink, readlink, fsync, inactive, fid, rwlock/rwunlock, seek, cmp, frlock, space, realvp, getpage/putpage, map/addmap/delmap, poll, dump, pathconf, pageio, dumpctl, dispose, secattr, shrlock, vnevent, reqzcbuf, retzcbuf.

`fshead_*()` functions cover VFS ops: mount, unmount, root, statvfs, sync, syncfs, vget, mountroot, freevfs, vnstate.

Each head function:
- Locks the object FEM head.
- If no stack exists, calls the current base op directly.
- Otherwise increments stack refcount, unlocks, initializes `femarg_t`/`fsemarg_t` at top-of-stack, finds a matching top operation, invokes it, then releases the stack.

## Next Operations
`vnext_*()` and `vfsnext_*()` are exported to monitor implementations. They:
- Decrement `fa_fnode` to move below the current monitor.
- Use `vsop_find()`/`vfsop_find()` to find the next monitor or base op.
- Assert valid function and target object.
- Invoke with the same logical operation arguments.

These are the canonical way for interposition modules to continue the operation chain.

## Stack Lifetime and Concurrency
`fem_lock()` / `fem_unlock()` protect a `fem_head`.
`fem_addref()` / `fem_delref()` use atomics for list lifetime.
`fem_get()` safely obtains a referenced current list.
`fem_release()` decrements the list refcount and, when zero, calls monitor argument release callbacks from top down before freeing the list.

This permits operations already in flight to continue on an old list while install/uninstall creates or swaps a new list.

## List Creation and Mutation
`new_femhead()` atomically installs a new head with CAS, preserving lock-free unaugmented fast paths.

`femlist_create()` allocates an uninitialized list with a placeholder guard.
`femlist_construct()` creates a list containing guard plus original base ops.
`fem_dup_list()` clones an existing stack and calls hold callbacks on cloned monitor arguments.

`fem_push_node()`:
- Validates monitor ops and opaque argument.
- Creates a head/list as needed.
- Expands stack capacity by cloning when full.
- Installs the head ops in the object’s `v_op`/`vfs_op` on first monitor push.
- Enforces install policy:
  - `FORCE`: always push.
  - `OPUNIQ`: reject if same ops vector already exists.
  - `OPARGUNIQ`: reject if same ops vector and opaque argument already exist.
- Appends the new node at top-of-stack.

`fem_remove_node()`:
- Finds a matching monitor by ops and optional data pointer.
- If list is idle, removes in place.
- If busy, clones list, removes from clone, and swaps current head.
- Restores base ops and clears list when the last monitor is removed.
- Calls release callbacks for removed monitor arguments.

## Public FEM API
Vnode interposition:
- `fem_create()`: builds a monitor vector from an operation template.
- `fem_install()`: pushes a monitor onto a vnode.
- `fem_is_installed()`: scans for a monitor/argument pair.
- `fem_uninstall()`: removes a monitor.
- `fem_setvnops()`: changes base vnode ops even when interposed.
- `fem_getvnops()`: returns base vnode ops under interposition.

VFS interposition:
- `fsem_create()`
- `fsem_install()`
- `fsem_is_installed()`
- `fsem_uninstall()`
- `fsem_setvfsops()`
- `fsem_getvfsops()`

VFS APIs require `vfs_implp` to be initialized.

## Initialization
`fem_init()`:
- Initializes null guard metadata.
- Creates vnode head ops via `vn_make_ops("fem-head", ...)`.
- Creates vnode guard monitor via `fem_create("fem-guard", ...)`.
- Creates VFS head ops via `vfs_makefsops(...)`.
- Creates VFS guard monitor via `fsem_create("fem-guard", ...)`.

## Integration Points
- Vnode/VFS operation registration: `vn_make_ops()`, `vfs_makefsops()`, `fs_build_vector()`.
- Core vnode fields: `v_op`, `v_femhead`.
- Core VFS fields: `vfs_op`, `vfs_femhead`, `vfs_implp`.
- Atomic and memory ordering primitives: `atomic_cas_ptr()`, `membar_consumer()`, `atomic_inc_32()`, `atomic_dec_32_nv()`.

## Risks and Subtle Areas
- Head functions are repetitive and must exactly match operation signatures; a mismatch corrupts call frames.
- Install/uninstall copy-on-update relies on correct refcount handling and hold/release callback symmetry.
- Removing the last monitor must restore base ops and free the list without disrupting in-flight callers.
- `fem_setvnops()` and `fsem_setvfsops()` must update base ops inside the stack when interposition is active.
- Guard ops panic intentionally; reaching them means stack underrun or corruption.
- `fem_push_node()` first monitor install changes object ops to head ops, so unaugmented objects stay fast until needed.

## Testing/Validation Signals
- Install one and multiple vnode monitors; verify call order and `vnext_*()` continuation.
- Install duplicate monitors under `FORCE`, `OPUNIQ`, and `OPARGUNIQ`.
- Uninstall while operations are in flight.
- Replace base vnode/VFS ops while a monitor is installed.
- VFS monitor install/uninstall on initialized and uninitialized VFS objects.
- Coverage across void-return operations as well as int-return operations.
