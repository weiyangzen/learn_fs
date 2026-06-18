<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/defs.h -->
## sources/test-tools/strace/src/defs.h

Purpose: Central strace internal header. It defines global configuration, core trace-control structures, result flags, syscall/personality abstractions, decoder declarations, printing helpers, fetch helpers, and common inline utilities used across syscall decoders.

Important APIs and types: Defines `MAX_ARGS`, personality word-size macros, `struct_ioctlent`, injection flags and `struct inject_data`/`struct inject_opts`, `struct tcb`, TCB and qualifier flags, `entering`/`exiting`/`syserror`/`verbose`/`abbrev` predicates, `RVAL_*` return formatting flags, pid/socket enums, many external xlat tables, decoder helper typedefs, mpers macros, `SYS_FUNC`, syscall range helpers, integer truncation helpers, `popcount32`, `ilog2_64`, `ilog2_32`, `printflags`/`printxval` wrappers, and `print_big_u64_addr`.

Control flow: Header-only but controls most decoder behavior through macros and inline functions. `SYS_FUNC(name)` establishes decoder signatures. Return-value flags steer the main syscall output machinery. Predicate macros read `struct tcb` flags to decide entry/exit, raw/verbose/abbrev handling, filtering, tampering, and delay state.

State and persistence: Declares process-global state such as current personality, word sizes, sysent/ioctl tables, inject vectors, `printing_tcp`, and personality names. `struct tcb` stores per-tracee syscall args, return/error state, timestamps, injection config, private decoder data, output streams, pid namespace metadata, delay state, seccomp/KVM/stacktrace fields, and command name cache.

Dependencies and integration: Includes architecture/config, kernel type, sysent, mpers, xlat, malloc, print-field, and syscall headers. Nearly every source in this subset depends on it directly or indirectly.

Risks: Extremely high blast radius. Small macro or struct changes can affect all decoders, mpers builds, multiple personalities, and output formatting. Word-size dispatch and pointer truncation must remain correct for compat tracing. TCB flag semantics are coupled to the tracing loop outside this file.

Test signals: Whole-suite build/test coverage is required after changes. Focused tests should include native and compat personalities, syscall entry/exit transitions, injected failures/delays/pokes, raw/abbrev/verbose qualifiers, return formatting, fd/pid/path printing, and mpers decoder compilation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/defs.h -->
