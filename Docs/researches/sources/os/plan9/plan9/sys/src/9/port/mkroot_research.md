# File Research: sources/os/plan9/plan9/sys/src/9/port/mkroot

Purpose: rc helper that embeds one boot file as an assembly root image.

Key logic:
- Usage: `mkroot path name`.
- Copies the file to `name.out`.
- Strips it if `file` reports it as executable.
- Runs `aux/data2s name` to produce `name.root.s`.

Dependencies and integration:
- Uses Plan 9 `file`, `strip`, `aux/data2s`, and build naming conventions.
