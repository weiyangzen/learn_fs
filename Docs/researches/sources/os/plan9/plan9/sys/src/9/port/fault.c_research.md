# File Research: sources/os/plan9/plan9/sys/src/9/port/fault.c

Purpose: Architecture-neutral virtual memory fault handling, demand paging, copy-on-write, address validation, and segment lookup.

Key logic:
- `fault` locates the user segment for an address, rejects invalid/write-to-readonly faults, and calls `fixfault`.
- `fixfault` handles segment types: text demand load, BSS/shared/stack zero-fill, data demand/page-in/copy-on-write, and physical mappings.
- `pio` loads pages from executable image or swap, handles races while segment locks are dropped, caches loaded pages, and zero-fills short image pages.
- `okaddr` and `validaddr` validate syscall user ranges across segments and post debug notes on invalid access.
- `vmemchr` searches memory while validating crossed user pages.
- `seg` finds a segment containing an address, optionally returning it locked.
- `checkpages` debug-checks mapped pages against MMU state.

Dependencies and integration:
- Uses `Segment`, `Page`, `Pte`, swap/image page cache, `newpage`, `putmmu`, `devtab` reads, process notes, and machine fault counters.

Risks and notes:
- `pio` deliberately drops the segment lock around I/O and rechecks races afterward.
- Copy-on-write behavior depends on page refs and swap refs.
- Physical segments can call architecture-specific page allocators.
