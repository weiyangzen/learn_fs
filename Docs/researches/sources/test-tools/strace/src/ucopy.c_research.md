# sources/test-tools/strace/src/ucopy.c

Purpose: low-level tracee memory read/write helpers used by decoders and injection.

Important APIs/types/functions: `umoven`, `umovestr`, `upoken`, `invalidate_umove_cache`, `process_read_mem`, `vm_read_mem`, `vm_write_mem`, `umoven_peekdata`, `umovestr_peekdata`, `upoken_pokedata`, and page cache helpers.

Control flow: read paths prefer `process_vm_readv`, cache up to four tracee pages for small same-page reads, and fall back to `PTRACE_PEEKDATA` on `ENOSYS` or permission failures. String reads avoid crossing pages so a NUL before an inaccessible page is still found. Write paths prefer `process_vm_writev` and fall back to `PTRACE_POKEDATA`, using read-modify-write for unaligned partial words.

State and persistence behavior: static booleans remember unsupported process_vm syscalls; a small static page cache stores recent remote page starts and buffers until `invalidate_umove_cache` is called before each new event.

Dependencies and integration points: core dependency for almost every syscall/ioctl decoder and injection poke logic; uses ptrace, process_vm syscalls, current word-size globals, page-size helper, and scno definitions.

Risks: stale memory cache must be invalidated at event boundaries. Partial reads/writes, tracee exit, inaccessible pages, compat address truncation, and unaligned pokes are high-risk. Fallbacks must distinguish expected tracee disappearance from real tracer errors.

Test signals: successful process_vm read/write, ENOSYS fallback, EPERM fallback, short read diagnostics, string NUL before page boundary, invalid compat address, unaligned write at beginning/end, tracee death (`ESRCH`), and cache invalidation across events.
