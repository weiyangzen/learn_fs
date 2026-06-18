# File Research: sources/os/plan9/9front/sys/src/9/port/mkroot

Single-file root embedding helper.

Key responsibilities:
- Expects `mkroot path name`.
- Copies the input to `<name>.out`.
- Strips it if `file` reports it as executable.
- Converts bytes to assembly data with `aux/data2s`, writing `<name>.root.s`.
- Prints progress messages.

Role:
- Older/single-file variant of the boot file embedding flow.
