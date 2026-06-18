# File Research: sources/os/bsd/openbsd-src/sys/kern/makesyscalls.sh

Read completely: 467 lines.

Shell/awk generator for OpenBSD syscall tables and headers. Given an input syscall master file, it generates syscall names, syscall numbers, syscall switch entries, and syscall argument structures.

Inputs and outputs:
- Requires exactly one input file and exits with usage otherwise.
- Emits `syscalls.c`, `../sys/syscall.h`, `init_sysent.c`, and `../sys/syscallargs.h`.
- Uses temporary files `sysent.dcl`, `sys.protos`, and `sysent.switch`, deleted via shell trap.
- Configurable variables include output paths, switch table name `sysent`, syscall name table `syscallnames`, constant prefix `SYS_`, and `compatopts`. This OpenBSD script explicitly does not support `LIBCOMPAT`.

Preprocessing:
- A `sed` stage removes dollar signs, joins backslash-continued lines, and inserts spaces around braces, parentheses, stars, and commas except preprocessor lines.
- The awk stage skips blank/comment lines, preserves includes and conditional preprocessor directives in generated outputs, and tracks nested `#if`/`#else`/`#endif` syscall number state.

Parsing and validation:
- Syscall numbers must be strictly synchronized with the first field; mismatches are fatal.
- `parseline()` handles optional `NOLOCK`, optional function alias, return type, function name, argument list, varargs marker, and a maximum of six syscall arguments.
- Argument metadata is used both for syscall switch argument size and for generated `struct <syscall>_args` definitions.
- Errors include unexpected tokens, unbalanced preprocessor conditionals, too many arguments, and unrecognized syscall keywords.

Generated content:
- Initializes standard generated-file comments and a `syscallarg(x)` macro with endian-aware padding.
- `putent()` writes prototypes, `struct sysent` entries, syscall names, syscall number defines, libc-lint prototype comments, and syscall argument structs.
- `STD`, `NODEF`, and `NOARGS` entries generate normal syscall switch entries with different header/argument-struct behavior.
- `OBSOL` and `UNIMPL` entries emit `sys_nosys` switch entries and human-readable names; obsolete entries still leave comments in the number header.
- Compatibility keywords would be mapped through generated wrapper macros if `compatopts` were populated.
- The END block closes generated arrays and defines `SYS_MAXSYSCALL`.

Build role:
- This is build-time source generation, not runtime kernel code.
- It is intentionally strict because the generated syscall ABI headers and dispatch table must remain numerically aligned with the master syscall list.
