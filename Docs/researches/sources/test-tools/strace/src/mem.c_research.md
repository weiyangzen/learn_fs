<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mem.c -->
# sources/test-tools/strace/src/mem.c

Purpose: decodes memory-management syscalls such as brk, mmap variants, mprotect, mremap, madvise, mlock, msync, mincore, remap_file_pages, mseal, and powerpc subpage protection.
Important APIs/types/functions: `get_pagesize`, `print_mmap_flags`, `print_mmap`, `SYS_FUNC(mmap*)`, `do_mprotect`, `process_madvise`, `print_mincore_entry`, many `xlat` tables, and `fetch_indirect_syscall_args`.
Control flow: syscall-specific printers emit arguments in kernel ABI order; old mmap fetches an indirect six-word vector; page-offset variants multiply by cached page size; exit-side mincore prints returned residency bits.
State and persistence behavior: caches page size statically; otherwise stateless. Dependencies and integration points: generic syscall dispatch, xlat tables, iovec printers, and architecture capability macros.
Risks: offset units differ by ABI, HPPA madvise constants have old/new meanings, and mincore element count depends on page-size rounding. Test signals: mmap offset tests, old mmap indirect tests, madvise HPPA cases, mincore success/error, mremap flag combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mem.c -->
