# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/doorfs/door_sys.c

## Purpose
Implements the illumos door system-call layer and kernel door interfaces. Doors are an RPC-like IPC mechanism where clients invoke server threads through door descriptors or kernel-held door handles. This file owns door syscall dispatch, creation/revocation, argument/result transfer, descriptor translation, server-thread shuttle scheduling, unref notifications, process exit/fork cleanup, and exported kernel interfaces such as `door_ki_create()`, `door_ki_upcall()`, and `door_ki_lookup()`.

## Main Responsibilities
- Registers the `doors` syscall module and optional 32-bit syscall entry.
- Creates synthetic door vnodes/files and tracks them in per-process door lists.
- Implements `door_call()` client invocation and `door_return()` server reply/wait loop.
- Moves data and descriptors between client/server address spaces using small-buffer copy or direct page copy.
- Handles user server pools, private door binding, cancellation, revocation, unref delivery, and process lifecycle cleanup.
- Provides kernel consumers with door handles, upcalls, parameter APIs, and reference management.

## Key Data and Limits
- `door_max_arg`: threshold for kernel-buffer copy versus direct page-copy transfer.
- `door_max_upcall_reply`: caps kernel door-upcall reply allocation.
- `door_max_desc`: caps descriptors passed per call/return.
- `door_knob`: global door mutex protecting door state, server pools, active counts, and unref lists.
- `door_node_t`: door object behind VDOOR vnodes, with target process, callback, flags, per-door private server pool, active call count, and limits.
- Per-thread `door_data_t` contains client/server substructures used while the thread is in a door call or server wait.

## System Call Dispatch
`doorfs()` switches on subcodes:
- `DOOR_CALL`
- `DOOR_RETURN`
- legacy `DOOR_RETURN_OLD`
- `DOOR_CREATE`
- `DOOR_REVOKE`
- `DOOR_INFO`
- `DOOR_BIND`
- `DOOR_UNBIND`
- `DOOR_UNREFSYS`
- `DOOR_UCRED`
- `DOOR_GETPARAM`
- `DOOR_SETPARAM`

The 32-bit path `doorfs32()` mirrors this and explicitly casts 32-bit pointer-sized arguments to avoid sign-extension problems.

## Door Creation and Lookup
`door_create()` validates attributes, calls `door_create_common()`, then marks the returned fd close-on-exec.

`door_create_common()`:
- Allocates `door_node_t` and a vnode.
- Initializes server process, callback, cookie, flags, descriptor/data limits.
- Installs `door_vnodeops`, marks vnode as `VDOOR`, attaches dummy `door_vfs`.
- Inserts the door into the server process list under `door_knob`.
- Allocates a `file_t` and optionally fd.
- Cleans up list/vnode/node on `falloc()` failure.

`door_lookup()` validates that an fd resolves, through `VOP_REALVP()` if needed, to a `VDOOR` vnode. Callers must `releasef()`.

## Invocation Flow
`door_call()`:
- Copies in `door_arg_t` or 32-bit equivalent.
- Looks up the door, takes a vnode hold, and drops the fd reference.
- Checks door validity and per-door data/descriptor limits.
- Handles kernel door servers directly in caller context when `door_target == &p0`.
- For user servers, obtains an available server thread via `door_get_server()`.
- Transfers args to the server through `door_args()`.
- Sets caller/server linkage, increments `door_active`, resumes the server by shuttle.
- Handles interrupted waits, SIGCANCEL delivery unless `DOOR_NO_CANCEL`, server exit, and late result races.
- Copies returned data/descriptors to user buffers or overflow mappings.
- Cleans up overflow mappings, descriptor arrays, file references, temporary buffers, kernel-server destructors, and vnode holds.

Important invariants:
- Client and server thread state is protected by `door_knob`.
- `DOOR_T_HOLD()` prevents a peer thread from exiting while data is copied.
- `door_active` delays unref delivery until in-flight calls finish.

## Server Return Flow
`door_return()`:
- Records the server stack base/size.
- If there is a caller, transfers results through `door_results()`.
- Places the server back in its pool with `door_release_server()`.
- Wakes the caller or switches back to wait for a new invocation.
- On a new call, invokes `door_server_dispatch()` to lay out and copy arguments on the server stack.
- Handles /proc stops, signals, cancellation, and server exit.

`door_server_dispatch()`:
- Computes stack layout with `door_layout()`.
- Inserts descriptors into the server process, copies descriptors/data onto the stack, and optionally emits `door_info_t` for private empty pools.
- Writes `door_results` or `door_results32`.
- Calls architecture helper `door_finish_dispatch()`.

`door_layout()` carefully checks overflow, stack alignment, descriptor/data/info/result placement, and recorded stack-size bounds.

## Data and Descriptor Transfer
- `door_args()` copies user client args to a user server. Small data uses a kernel buffer; larger data copies directly page-by-page into the server stack with `door_copy()`.
- `door_results()` copies server results back to the caller, handles upcall reply limits, overflow mapping, direct copy, and descriptor translation.
- `door_overflow()` maps a new anonymous region in the caller address space when the original result buffer is too small.
- `door_copy()` locks the destination user page, maps it into kernel space, and uses `copyin_nowatch()` from the current address space.

Descriptor helpers:
- `door_insert()` allocates an fd in the current process for a returned `file_t` and fills `door_desc_t` attributes.
- `door_translate_in()` converts user fds to kernel door handles for kernel servers.
- `door_translate_out()` converts kernel descriptors/handles into held `file_t` references for user delivery.
- `door_fd_close()`, `door_fd_rele()`, `door_release_fds()`, and `door_fp_close()` centralize cleanup of descriptor/file ownership.

## Server Pools and Binding
`door_get_server()` scans a door-private pool or process-wide pool for a server thread sleeping on `SOBJ_SHUTTLE`; if unavailable, waits interruptibly on the pool CV. It removes the selected server from the pool and marks it runnable/onproc.

`door_release_server()` returns a server to its pool and signals waiters.

`door_bind()` binds the current LWP to a private door pool and increments the door-bound thread count through `door_bind_thread()` in `door_vnops.c`.

`door_unbind()` reverses binding or clears invalid inherited binding state.

## Revocation, Exit, Fork, and Unref
- `door_revoke()` marks a current-process door revoked, wakes server waiters, drops the fd using `closeandsetf()`.
- `door_revoke_all()` marks all current-process doors revoked before thread termination.
- `door_exit()` clears process door/unref lists during final process exit.
- `door_slam()` handles current thread exit during active door work, waking a caller with `DOOR_EXIT` and implicitly unbinding private doors.
- `door_fork()` marks inherited private bindings invalid in `forkall()` children.
- `door_deliver_unref()` queues unreferenced-door notifications and holds the vnode while queued.
- `door_unref()` and `door_unref_kernel()` drain per-process or process-0 unref queues and deliver user/kernel callbacks.

## Parameter and Info APIs
- `door_setparam()` / `door_getparam()` and kernel variants control/read max descriptors, min data, and max data.
- `door_check_limits()` enforces per-door limits, with unref upcall exception for data minimum.
- `door_info()` / `door_info_common()` fill `door_info_t`, including `DOOR_LOCAL`, uniquifier, attributes, and inferred `DOOR_IS_UNREF`.
- `door_ucred()` returns caller credentials to a server, using upcall credentials when present.

## Kernel Interfaces
Exports:
- `door_ki_create()`
- `door_ki_upcall()`
- `door_ki_upcall_limited()`
- `door_ki_hold()`
- `door_ki_rele()`
- `door_ki_open()`
- `door_ki_info()`
- `door_ki_lookup()`
- `door_ki_setparam()`
- `door_ki_getparam()`

These adapt kernel `door_handle_t` values to `file_t *`, preserve references, and invoke the same core upcall/parameter/info machinery.

## Integration Points
- Door vnode operations from `door_vnops.c`.
- VFS/vnode/file table routines: `vn_alloc`, `vn_setops`, `falloc`, `getf`, `releasef`, `closef`, `closeandsetf`.
- Scheduler/thread shuttle routines: `shuttle_resume`, `shuttle_swtch`, `shuttle_sleep`.
- VM/address-space APIs: `as_pagelock`, `as_map`, `as_unmap`, `hat_kpm_mapin`, `ppmapin`.
- /proc and signal machinery: `prstop`, `ISSIG`, `sigtoproc`, `schedctl_cancel_pending`.
- Credential conversion via `cred2ucred()`.

## Risks and Subtle Areas
- Reference ownership is complex: fd refs, file refs, vnode refs, descriptor release flags, and door handles must match every success/error path.
- `door_knob` lock ordering is critical; many helpers assert it is held or not held.
- Interrupt/cancel/server-exit paths are race-sensitive and use peer holds to avoid exit during copy.
- Stack layout arithmetic must avoid wraparound and preserve ABI alignment.
- Overflow result mappings must be unmapped on error to avoid user address leaks.
- Kernel-server destructor callbacks must run exactly once after returned data handling.

## Testing/Validation Signals
Useful coverage would include:
- User door call/return with small and large data.
- Descriptor passing with and without `DOOR_RELEASE`.
- 32-bit client compatibility.
- Private door binding/unbinding.
- Revocation while clients wait.
- Client interruption and `DOOR_NO_CANCEL`.
- Unref notification delivery for single and multi-unref modes.
- Kernel `door_ki_*` creation/upcall/open/info/param paths.
