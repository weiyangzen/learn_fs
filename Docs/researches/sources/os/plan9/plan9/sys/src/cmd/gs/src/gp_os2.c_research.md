# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os2.c

Read status: complete.

Purpose: OS/2 and MS-DOS platform support for Ghostscript when compiled with GCC/EMX or IBM C.

Major areas:
- OS/2/DOS platform lifecycle and environment setup.
- File enumeration.
- Printer and spooler support.
- Scratch file creation.
- Path-combine helper semantics.
- Cache and font enumeration stubs.

Main logic:
- Provides `gp_strerror`, `gp_get_realtime`, and `gp_get_usertime`.
- `gp_file_is_console` detects DOS console via ioctl when not OS/2; OS/2 treats descriptors 0-2 as console.
- Cache functions are stubs.
- Defines path/file constants: list separator `;`, scratch prefix `gs`, null `nul`, current directory `.`, binary suffix/modes.
- `gp_enumerate_files_init` stores OS/2 pattern and path head.
- `gp_enumerate_files_next` uses `DosFindFirst`/`DosFindNext` in OS/2 mode, but in DOS mode can only return the pattern once.
- `gp_init` may reconstruct DLL environment from the OS/2 process information block, invokes `_emxload_env("GS_LOAD")`, and installs a `SIGFPE` handler.
- `gp_exit` frees reconstructed environment for EMX DLL builds.
- `gp_open_printer` handles default spool, `\\spool\queue`, pipe commands, normal files, ports, and DOS `PRN`.
- `gp_close_printer` closes/pcloses and spools/deletes temporary files for spool targets.
- `pm_find_queue` enumerates OS/2 print queues and resolves default/specific queues and drivers.
- `pm_spool` opens an OS/2 spool queue, copies a temporary file to it with `SplQmWrite`, and ends/aborts the job.
- `gp_open_scratch_file` uses `_tempnam` under IBM C or `gp_gettmpdir` + `mktemp` + `gp_fopentemp` otherwise.
- Path helpers implement DOS/Windows-like root/separator/current/parent behavior.
- Font enumeration functions are stubs.

Filesystem/storage relevance:
- Full platform file, temporary-file, enumeration, pipe, and printer-spool backend for OS/2.

Notable behavior:
- Supports both OS/2 and DOS behavior paths via `isos2`.
- Uses legacy OS/2 spooler APIs and manual memory allocation with `DosAllocMem`.
- Uses `mktemp` in non-IBM-C scratch path.
