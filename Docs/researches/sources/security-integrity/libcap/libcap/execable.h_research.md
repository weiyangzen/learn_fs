## sources/security-integrity/libcap/libcap/execable.h

Purpose: macro/header machinery for making a shared object directly executable through a custom `__so_start` entry and embedded interpreter path.

Important APIs/macros/functions: `__execable_dl_loader` in `.interp`, weak `_IO_stdin_used` for glibc, `__execable_parse_args()`, `__SO_FORCE_ARG_ALIGNMENT`, `EXECABLE_INITIALIZE`, and `SO_MAIN`.

Control flow: `__so_start` reconstructs argv from `/proc/self/cmdline`, runs optional initialization, calls the file's static `__execable_main`, frees reconstructed argv memory, and exits. Argument parsing reads cmdline into a growing buffer and splits NUL-delimited entries.

State/persistence: allocates temporary argv memory; embeds loader path in the shared object; reads `/proc/self/cmdline`.

Dependencies/integration: Linux procfs, ELF `.interp`, glibc compatibility symbol, compiler attributes, Makefile-provided `SHARED_LOADER`.

Risks: Linux/ELF-specific and assumes `/proc` availability; direct shared-object execution can be fragile across loaders/architectures; argv reconstruction exits process on allocation failure.

Test signals: direct execution tests for `libcap.so`, `libpsx.so`, and `pam_cap.so`; run with/without arguments under glibc targets.
