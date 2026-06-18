# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/time/compat_localtime.c

Read completely: 91 lines.

This builds many old time APIs, including `gmtime_r`, `localtime_r`, `mktime_z`, `timegm`, `timelocal`, `tzset`, and related conversion helpers, by redefining time types to compatibility layouts and including `time/localtime.c`. Because it must include `<sys/stat.h>` under `__LIBC12_SOURCE__`, it manually declares current `stat`/`fstat` as `__stat50`/`__fstat50` so included timezone code can use current file metadata.

Important interactions: this is a source-level ABI specialization of the shared timezone implementation.

Security/reliability notes: inherits the complexity of `localtime.c`; old callers see 32-bit `time_t` limits even though the included code uses current stat calls internally.
