# File Research: sources/teaching/os161/kern/include/proc.h

Defines the process structure and process lifecycle interface.

Key structure:
- `struct proc` stores name, spinlock, thread count, address space pointer, and current working directory vnode.
- Comments note `p_addrspace` must be spinlock-protected because context switch may read it without sleeping.

Key APIs:
- Bootstrap, create runprogram process, destroy.
- Add/remove thread.
- Get/set current process address space.
- Exposes `kproc`.

Relevance:
- VFS path resolution uses process current working directory.
- `current.h` exposes `curproc` as current thread’s process.
