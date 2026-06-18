# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_subr.c

## Purpose
Provides common exec VM-command and stack setup helpers used by executable format loaders.

## Main Interfaces
- `new_vmcmd()` appends a VM command and references any vnode it carries.
- `vmcmdset_extend()` grows VM command storage.
- `kill_vmcmds()` releases vnode references and frees VM command arrays.
- `vmcmd_map_pagedvn()` maps demand-paged vnode-backed executable segments.
- `vmcmd_map_readvn()` allocates anonymous memory then reads file data into it.
- `vmcmd_readvn()` performs user-space segment reads and adjusts protections.
- `vmcmd_map_zero()` maps zero-filled memory, including stack regions.
- `exec_read()` reads exact-size executable data from a vnode.
- `exec_setup_stack()` builds accessible stack, inaccessible growth reservation, and guard mappings.

## Dependencies
Uses UVM maps/objects, vnode mapping/access operations, PaX mprotect and ASLR stack hooks, process resource limits, stack-direction macros, and exec package VM command structures.

## Implementation Notes
`vmcmd_get_prot()` centralizes requested/max protection calculation and PaX validation. `exec_setup_stack()` supports 32-bit stack limits through `EXEC_32`, applies stack ASLR, and creates separate guard, inaccessible, and accessible stack VM commands.

## Research Notes
This file is shared by multiple executable loaders. Changes to protection handling or VM command lifetime can affect all exec formats, demand paging, W^X enforcement, stack layout, and vnode reference safety.
