# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslib.h

Declares the Ghostscript library initialization/finalization API. `gs_lib_init` performs full initialization using the C heap by default, while `gs_lib_init0` and `gs_lib_init1` split initialization so clients can substitute a different allocator after phase 0.

`gs_lib_finit` performs cleanup after execution and accepts exit status, error code, and memory pointer. The header requires stdio and Ghostscript memory definitions from its includer context.
