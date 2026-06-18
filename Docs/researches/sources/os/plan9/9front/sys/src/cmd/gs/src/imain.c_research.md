# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/imain.c

Provides common top-level support for Ghostscript interpreter front ends.

Key points:
- `get_minst_from_memory` retrieves the interpreter instance through library context backpointers.
- `gs_main_alloc_instance` allocates and initializes `gs_main_instance`.
- `gs_main_init0`:
  - calls platform init
  - resets debug flags
  - records base time
  - allocates library path containers
- `gs_main_init1`:
  - initializes interpreter allocator spaces
  - initializes library level 1
  - initializes save machinery
  - creates name table and roots it
  - calls `obj_init`
  - initializes plugins
- `gs_main_init2`:
  - runs `zop_init`
  - initializes IO devices
  - calls `op_init`
  - publishes `INITFILES`, `EMULATORS`, and `LIBPATH`
  - runs the standard init file or compiled init string
  - sets display callback if present
  - initializes readline
- `gs_main_interpret` wraps `gs_interpret` and handles `e_NeedStdin`, `e_NeedStdout`, and `e_NeedStderr` callouts by moving data through interpreter stacks and resuming with a null ref plus `zpop`.
- Search path helpers:
  - `gs_main_add_lib_path`
  - `gs_main_set_lib_paths`
  - `gs_main_lib_open`
- Execution helpers:
  - `gs_main_run_file`
  - `gs_main_run_file_open`
  - `gs_main_run_string`
  - `gs_main_run_string_with_length`
  - suspendable string begin/continue/end
- Operand stack C API:
  - `gs_push_boolean/integer/real/string`
  - `gs_pop_boolean/integer/real/string`
- `gs_main_finit`:
  - collects temporary filenames
  - performs final global reclaim
  - uninstalls page device and closes current device
  - flushes stdout/stderr files
  - finalizes readline
  - restores all allocations
  - finalizes plugins
  - closes redirected stdout
  - unlinks temp files
  - calls `gs_lib_finit`
- Provides `gs_to_exit`, `gs_to_exit_with_code`, `gs_abort`, resource-usage printing, and stack dumping.

Dependencies and interactions:
- Calls `iinit.c`, interpreter core, allocator/save machinery, plugin system, devices, file/path code, and error codes.
- Front-end API documented in `imain.h` and driven by `imainarg.c`.

Risks and notes:
- Header comments call instance lookup from memory a hack.
- Some init and platform/device behavior is order-sensitive.

Research relevance:
- Main lifecycle engine for embedding/running/finalizing the Ghostscript interpreter.
