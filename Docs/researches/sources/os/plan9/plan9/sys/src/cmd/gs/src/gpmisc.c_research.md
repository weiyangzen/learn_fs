# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpmisc.c

Purpose: Provides generic platform support helpers shared by Ghostscript `gp_` implementations: temporary directory lookup, safe temp-file opening, and portable pathname combination/reduction.

Key interfaces: `gp_gettmpdir`, `gp_fopentemp`, `gp_file_name_combine_generic`, `gp_file_name_reduce`, `gp_file_name_is_absolute`, `gp_file_name_parents`, and `gp_file_name_cwds`.

Control flow: temp lookup checks `TMPDIR` then `TEMP` using the `gp_getenv` contract. `gp_fopentemp` parses stdio mode flags into `open` flags and uses `O_EXCL` plus user-only permissions before `fdopen`. Path combination walks prefix and filename components with platform-provided root/separator/current/parent hooks, collapses current and parent references when allowed, handles buffer-size reporting, and appends a NUL.

Dependencies: Relies on platform-specific functions from `gp.h` such as `gp_file_name_root`, separator predicates, current/parent rules, and `gp_file_name_combine`.

Risks and notes: The path reducer is shared across platforms and intentionally delegates syntax details. `gp_fopentemp` is safer than `mktemp`, but callers still must provide a unique name template.
