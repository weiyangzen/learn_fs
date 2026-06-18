# File Research: sources/os/bsd/openbsd-src/sys/kern/exec_subr.c

Shared exec vmcmd helpers.

Key behavior:
- `new_vmcmd()` appends a vm command and holds referenced vnodes.
- `vmcmdset_extend()` doubles vmcmd storage.
- `kill_vmcmds()` releases vnode references and resets command storage.
- `exec_process_vmcmds()` executes vmcmds, handles relative mappings, and then clears the set.
- `vmcmd_map_pagedvn()` maps page-aligned executable segments directly from vnode objects with copy-on-write/fixed mapping.
- `vmcmd_map_readvn()` maps memory, reads bytes from a vnode into userspace, then restores requested protections.
- `vmcmd_map_zero()` maps anonymous zero-filled regions, including stacks.
- `vmcmd_mutable()` clears immutability over a region.
- `vmcmd_randomize()` fills a user region with random bytes, chunking large regions.
- `exec_setup_stack()` computes randomized stack bounds and emits guard plus writable stack vmcmds.

Filesystem/OS relevance:
- Bridges executable vnodes to UVM mappings.
- Central to demand-paged executable loading and non-demand-paged segment reads.
