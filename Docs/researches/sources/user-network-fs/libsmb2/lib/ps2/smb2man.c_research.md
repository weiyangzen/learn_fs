<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/smb2man.c -->
# sources/user-network-fs/libsmb2/lib/ps2/smb2man.c

## Purpose

`smb2man.c` is the PS2 IRX module wrapper for SMB2MAN. It declares module identity, starts the filesystem driver, and provides libc-style allocation shims backed by PS2 IOP system memory.

## Important APIs, Types, And Functions

The module defines `IRX_ID(MODNAME, VER_MAJOR, VER_MINOR)`, `_start`, `malloc`, `free`, and `calloc`. `_start` prints the module version and delegates to `SMB2_initdev`. Allocation wrappers call `AllocSysMemory` and `FreeSysMemory` while interrupts are suspended.

## Control Flow

Module load enters `_start`, ignores arguments, prints a banner, and returns the result of driver registration. `malloc` suspends interrupts, allocates with `ALLOC_FIRST`, resumes interrupts, and returns the pointer. `free` mirrors that for deallocation. `calloc` multiplies count and size, allocates, zeroes, and returns.

## State And Persistence Behavior

No persistent state is stored here. Memory allocation affects global IOP heap state. The IRX module remains resident or not according to the return code from `SMB2_initdev`.

## Dependencies And Integration Points

The file depends on PS2SDK kernel, loadcore, sysmem, and C library headers plus `smb2_fio.h`. Its allocation symbols satisfy code in this module build that expects standard C allocators.

## Risks And Edge Cases

`calloc` does not handle multiplication overflow and calls `memset` even if `malloc` returns `NULL`. Interrupt suspension around allocator calls is platform-specific and can increase interrupt latency. `malloc` takes `int size` while `calloc` computes `size_t`, so large allocations can truncate. There is no `realloc` shim.

## Test Signals

PS2 module tests should verify successful IRX load/unload behavior, driver registration result propagation, allocation failure handling, zeroed `calloc` memory for normal sizes, and behavior under low IOP memory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/smb2man.c -->
