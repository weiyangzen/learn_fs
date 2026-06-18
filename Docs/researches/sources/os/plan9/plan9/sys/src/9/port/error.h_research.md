# File Research: sources/os/plan9/plan9/sys/src/9/port/error.h

Purpose: Shared extern declarations for kernel error-string symbols.

Contents:
- Declares common Plan 9 kernel error strings such as mount errors, filesystem lookup errors, permission errors, fd errors, I/O errors, memory errors, networking errors, media-change errors, USB endpoint errors, and AoE-down errors.
- Used by kernel/device code to raise stable textual errors through `error()` without duplicating string definitions.

Dependencies and integration:
- Consumed broadly by device, filesystem, VM, and syscall code.
- `mkerrstr` transforms this file into error-string definitions.
