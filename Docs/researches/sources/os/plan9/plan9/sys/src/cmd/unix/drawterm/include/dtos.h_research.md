# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/dtos.h

Host-selection wrapper for drawterm OS compatibility headers.

Key contents:
- Includes `unix.h` for Unix-like systems and `9windows.h` for Windows.
- On Apple builds, aliases `panic` to `dt_panic`.
- Defines `main` as `mymain` on Windows.
- Errors out if no supported OS macro is defined.

Role in this group:
- Bridges drawterm’s Plan 9 compatibility layer to host OS headers.

Notable risks:
- Platform selection is preprocessor-macro dependent and reflects older OS naming conventions.
