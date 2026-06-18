# File Research: sources/teaching/xv6-riscv/kernel/exec.c

Implements `kexec()`, the kernel side of `exec`.

Important behavior:
- Opens an executable through `namei()` inside a filesystem transaction.
- Validates `ELF_MAGIC`, iterates program headers, allocates user memory, and loads segments with `loadseg()`.
- `flags2perm()` maps ELF write/execute flags to PTE bits.
- Builds a guarded user stack and copies argument strings/pointers with `copyout()`.
- Commits the new process image only after all allocation and loading succeeds.
- Frees the old page table after switching `p->pagetable`, `p->sz`, `epc`, and `sp`.

Filesystem relevance: this is a key consumer of inode reads. It relies on `readi()`, path lookup, inode locking, and log transaction boundaries, linking filesystem namespace state to process image creation.
