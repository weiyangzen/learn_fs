# File Research: sources/os/bsd/netbsd-src/lib/libexecinfo/backtrace.c

## Purpose
Implements symbol formatting for `backtrace(3)` results and sandbox-friendly initialization of executable access.

## Main Components
- `open_self()` opens the current executable via `/proc/self/exe` on Linux or `/proc/curproc/file` on NetBSD, with a `sysctl(KERN_PROC_PATHNAME)` fallback when available.
- `backtrace_sandbox_init()` opens and caches the executable fd before sandboxing; `backtrace_sandbox_fini()` closes it.
- `rasprintf()` grows a formatting buffer around `vsnprintf()`.
- `format_string()` supports `%a`, `%n`, `%d`, `%D`, and `%f` substitutions for address, symbol name, offset, conditional offset, and filename.
- `format_address()` combines `dladdr()` with optional ELF symbol-table lookup from `symtab.c`.
- `backtrace_symbols_fmt()` creates one allocation containing the pointer array and formatted strings.
- `backtrace_symbols_fd_fmt()` writes formatted symbols to a supplied fd.
- `backtrace_symbols()` and `backtrace_symbols_fd()` use the default format `%a <%n%D> at %f`.

## Integration
Relies on `dladdr()`, libelf-backed `symtab_create/symtab_find`, and architecture canonicalization from `symbol.h`.

## Risks / Notes
- Uses offsets during allocation because `realloc()` can move the combined array/string buffer.
- If the executable cannot be opened or has no usable symbol table, it falls back to `dladdr()` and placeholder strings.
- `backtrace_sandbox_fini()` asserts the cached fd is valid.
