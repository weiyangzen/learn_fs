# File Research: sources/os/bsd/dragonflybsd/sys/kern/imgact_resident.c

## Summary
Implements resident executable support: privileged processes can snapshot an executable's VM space so later execs of that vnode reuse the resident VM image instead of loading from disk.

## Main Responsibilities
- Maintains a global `exec_res_list` protected by `exec_list_lock`.
- Exposes `vm.resident` sysctl reporting resident executable IDs, paths, entry addresses, and stat data.
- Provides `exec_resident_imgact()` image activation for vnodes with `v_resident`.
- Implements `exec_sys_register` and `exec_sys_unregister` syscalls.

## Important Behavior
Registration requires `SYSCAP_NOVM_RESIDENT`, uses the current process text vnode, holds the vnode, forks the current `vmspace`, initializes its pmap, stores syscall vector and entry address, and links the resident record to `vp->v_resident`.

Activation increments `vr_refs` while under shared list lock, switches the exec target to the resident `vmspace` with `exec_new_vmspace`, sets `imgp->resident`, `p_sysent`, and `entry_addr`, then decrements the ref.

Unregister supports current process (`id == -1`) and all entries (`id == -2`), waiting briefly when `vr_refs` indicates an exec race.

## Risks
Resident entries tie vnode lifetime, VM space lifetime, entry address, and syscall vector together. The unregister wait loop uses `tsleep(..., 1)` polling and depends on `vr_refs` dropping promptly.
