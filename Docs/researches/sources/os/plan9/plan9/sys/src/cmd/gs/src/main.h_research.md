# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/main.h

`main.h` is a backward-compatible interface shim for older Ghostscript clients of `gsmain.c`. It includes `iapi.h`, `imain.h`, and `iminst.h`.

All compatibility macros and declarations are inside `#if 0`, so this version effectively only provides the include guard and the newer main API headers. The disabled block maps old single-interpreter APIs such as `gs_init0`, `gs_run_file`, and `gs_run_string` onto `gs_main_instance_default()` calls.

The file documents a removed compatibility layer while preventing old include paths from failing. There is no active runtime behavior beyond included declarations.
