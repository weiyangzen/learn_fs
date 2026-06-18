<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_winsize.c -->
# sources/test-tools/strace/tests/ioctl_winsize.c

Purpose: Tests decoding of terminal window-size ioctls `TIOCGWINSZ` and `TIOCSWINSZ`.

Important APIs/types/functions: Uses `ioctl`, `struct winsize`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `fill_memory`, and `sprintrc`.

Control flow: Issues NULL getter and setter calls, then uses a tail-allocated `winsize` and an immediately faulting pointer. It expects failed getter output to remain a pointer and setter output to decode `{ws_row, ws_col, ws_xpixel, ws_ypixel}` on entry.

State/persistence behavior: Uses fd `-1`, so no tty state is changed. All data is local memory.

Dependencies: Requires tty ioctl constants and the strace test helper library.

Integration points: Small regression test for ioctl direction semantics on terminal window-size structures.

Risks: Misclassifying `TIOCGWINSZ` as input or dereferencing output buffers on failed syscalls would produce wrong output.

Test signals: Lines for NULL, fault pointer, raw output pointer, decoded setter struct, and clean exit.

Source read signal: complete file read for this research pass; file size 43 line(s), 1052 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_winsize.c -->
