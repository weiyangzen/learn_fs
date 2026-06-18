# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-win32/wstrtoutf.c

Same wide-rune to UTF-8 helper as the OS X backend.

Key responsibilities:
- Computes UTF-8 length for a NUL-terminated `Rune` string.
- Converts `Rune` text to UTF-8 into a bounded buffer.

Role in this group:
- Supports Win32 Unicode clipboard conversion in `screen.c`.

Notable risks:
- Contains the same uninitialized `i` edge case when the output buffer is too small before converting any rune.
