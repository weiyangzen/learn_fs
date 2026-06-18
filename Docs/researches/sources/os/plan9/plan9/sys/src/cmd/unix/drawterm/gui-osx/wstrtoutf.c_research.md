# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-osx/wstrtoutf.c

Wide-rune to UTF-8 conversion helper shared with the Win32 GUI backend.

Key responsibilities:
- `wstrutflen()` computes the UTF-8 byte length of a NUL-terminated `Rune` string.
- `wstrtoutf()` converts a NUL-terminated `Rune` string into a UTF-8 byte buffer, returning required or written size depending on available space.

Role in this group:
- Used by platform clipboard paths that receive UTF-16/`Rune` text and need Plan 9 UTF strings.

Notable risks:
- In the buffer-too-small branch, `i` can be read before assignment if the first rune does not fit, so the reported required length can be undefined in that edge case.
- Assumes `Rune` storage is compatible with the platform data being passed in.
