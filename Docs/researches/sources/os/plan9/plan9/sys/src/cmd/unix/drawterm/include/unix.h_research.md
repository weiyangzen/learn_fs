# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/unix.h

Unix host compatibility header.

Key contents:
- Defines feature-test macros for BSD/SVID/XOpen and large-file behavior.
- Includes standard Unix/POSIX C headers and optionally pthreads.
- Defines `p9_vlong`, `p9_uvlong`, and `uintptr`.

Role in this group:
- Supplies host definitions before Plan 9 type and syscall remapping on Unix-like drawterm builds.

Notable risks:
- Feature-test macros are old and broad; they can interact poorly with modern libc header expectations.
