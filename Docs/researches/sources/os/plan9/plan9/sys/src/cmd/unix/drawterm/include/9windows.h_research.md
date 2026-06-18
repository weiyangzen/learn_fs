# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/9windows.h

Windows host compatibility header for drawterm’s Plan 9 portability layer.

Key contents:
- Includes standard C, Win32-ish POSIX compatibility, process, time, assert, and varargs headers.
- Disables selected MSVC warnings.
- Defines `p9_vlong`, `p9_uvlong`, and `uintptr` for Windows builds.

Role in this group:
- Included by `u.h` when `WINDOWS` is defined to supply host types and headers before Plan 9 type remapping.

Notable risks:
- Uses MSVC-specific `__int64` and assumes the older Windows build environment expected by drawterm.
