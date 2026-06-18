<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/perf.c -->
# sources/test-tools/strace/src/perf.c

Purpose: decodes `perf_event_open` and shared `perf_event_attr` structures for syscall and ioctl paths.

Important APIs/types/functions: `fetch_perf_event_attr`, `print_perf_event_attr`, `SYS_FUNC(perf_event_open)`, `struct pea_desc`, `free_pea_desc`, and perf xlat tables for type, config, sample/read formats, branch samples, breakpoints, and flags.

Control flow: on syscall entry it fetches the user attr size and stores a copied `perf_event_attr` in tcb private data; on exit it prints fields as the kernel sees them, including E2BIG size changes, type-specific `config` decoding, bit flags, optional versioned fields, breakpoint config, branch/sample register fields, aux action fields, and trailing data marker.

State and persistence behavior: per-syscall tcb private data owns a heap copy of the attr and is freed by `free_pea_desc`.

Dependencies and integration points: used by `perf_event_open` and `perf_ioctl.c`; depends on `perf_event_struct.h`, many perf xlat tables, tcb private data, and syscall enter/exit sequencing.

Risks: perf attr is versioned and accepts partial structures; field availability checks must mirror kernel behavior. Bitfield layout and new flags require ongoing updates.

Test signals: perf_event_open for hardware/software/cache/raw/breakpoint types, abbrev/full output, E2BIG size update, versioned optional fields, unknown reserved bits, invalid sizes, and ioctl modify-attributes reuse.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/perf.c -->
