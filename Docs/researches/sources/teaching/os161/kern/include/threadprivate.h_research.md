# File Research: sources/teaching/os161/kern/include/threadprivate.h

Declares thread subsystem internals that must be visible to machine-dependent code. It is placed in the public include directory only because architecture-specific thread code needs it.

Exports `thread_startup`, machine-dependent thread init/cleanup, assembler context switching via `switchframe_switch`, and `switchframe_init` for new thread setup. The types are forward declared: `struct thread`, `struct thread_machdep`, and `struct switchframe`.

This file is the boundary between portable thread management and architecture-specific saved-register frames. It should be used only by the thread subsystem; external users would couple themselves to scheduler internals.
