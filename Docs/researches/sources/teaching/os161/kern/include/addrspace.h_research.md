# File Research: sources/teaching/os161/kern/include/addrspace.h

Declares the process address-space abstraction and ELF loader interface.

Key contents:
- `struct addrspace` has concrete fields only under `OPT_DUMBVM`: two load regions and one stack physical base. Otherwise it is a placeholder for student VM implementation.
- Declares address-space lifecycle: create, copy, activate, deactivate, destroy.
- Declares region/load setup: define region, prepare load, complete load, define stack.
- Declares `load_elf(struct vnode *, vaddr_t *)`.

Relevance:
- Filesystem/vnode code supplies executable vnodes consumed by `load_elf`.
- Process and VM code use this as the boundary between VFS executable loading and address-space population.
