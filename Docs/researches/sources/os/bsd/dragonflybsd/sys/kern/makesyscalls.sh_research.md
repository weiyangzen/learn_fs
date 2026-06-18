# File Research: sources/os/bsd/dragonflybsd/sys/kern/makesyscalls.sh

## Scope

This shell script generates DragonFlyBSD syscall metadata and C headers/tables from a `syscalls.master`-style input file, optionally parameterized by a configuration file.

## Public And Internal APIs Covered

- Inputs: required syscall master file and optional config file sourced by the script.
- Generated outputs by default: `syscalls.c`, `../sys/sysproto.h`, `../sys/sysunion.h`, `../sys/syscall.h`, `../sys/syscall.mk`, and `init_sysent.c`.
- Temporary files: syscall declarations, compat declarations, switch entries, include fragments, argument structs, and syscall union fragments.
- Configurable symbols: syscall prefix, switch table name, names array name, header guard, and output paths.

## Control Flow And Behavior

- The script exits on error and registers a trap to remove temporary files.
- It preprocesses the master file with `sed`: removes dollar signs, joins backslash-continuation lines, and spaces punctuation tokens for easier AWK parsing.
- The AWK program writes boilerplate "DO NOT EDIT" headers for all generated files.
- Preprocessor include/conditional lines are copied into the appropriate generated fragments while preserving syscall number state across `#if`/`#else`.
- The parser validates monotonically increasing syscall numbers and emits an error if the current line number does not match the expected syscall index.
- `parseline()` handles syscall signatures, optional function aliases, argument aliases, and return types. It extracts argument type/name pairs and computes argument struct size macros.
- For `STD`, `NODEF`, `NOARGS`, `NOPROTO`, and `NOIMPL` entries, it emits argument structs where needed, syscall prototypes, sysent table rows, syscall name strings, syscall number defines, and makefile object names.
- `NOIMPL` maps the sysent handler to `sys_nosys` while preserving the exposed name.
- `OBSOL` emits obsolete comments and `sys_nosys` table rows.
- `UNIMPL` emits unnamed `#number` syscall names and `sys_nosys` rows.
- At END, it emits `AS()` sizing macro, optional compat macro, closing guards/braces, and `SYS_MAXSYSCALL`, then concatenates fragments into final output files.

## State And Data Structures

- AWK variables track `syscall`, saved syscall index across preprocessor branches, parsed argument arrays, aliases, return type size, generated file paths, and duplicate `nosys`/`lkmnosys` emission state.
- Generated `struct sysent` entries include argument size, return size, and function pointer cast.
- Generated `union sysunion` contains per-syscall argument structs for messaging.

## Dependencies

- Requires POSIX shell, `sed`, `awk`, and DragonFlyBSD syscall master syntax.
- The generated files are consumed by kernel syscall dispatch, syscall prototypes, syscall number headers, syscall name tables, and syscall object build lists.

## Risks And Invariants

- The master file's syscall numbers must remain contiguous with parser state, including across conditional sections.
- Function signatures must match the parser's expected brace/semicolon/parenthesis token layout.
- Temporary file cleanup depends on the trap and unique `$$` suffixes.
- Generated files are authoritative build artifacts; manual edits are overwritten by rerunning the script.
