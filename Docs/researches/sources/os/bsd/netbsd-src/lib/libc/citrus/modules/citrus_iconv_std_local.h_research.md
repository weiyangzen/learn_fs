# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_std_local.h

Read completely: 81 lines.

This header defines private data structures for `iconv_std`: per-encoding handles plus live/saved states, destination mapper records, source mapper records, shared converter state, and per-context state.

Important fields: `_citrus_iconv_std_shared` owns source/destination standard encodings, source charset mapping list, and invalid replacement policy; `_citrus_iconv_std_context` owns the per-call mutable encoding state wrappers.

Security/reliability notes: no executable code. The separation between shared immutable mapping state and per-context mutable conversion state is important for thread-safety and reentrancy.
