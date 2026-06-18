# File Research: sources/os/plan9/9front/sys/src/9/port/mkdevlist

Small `rc`/`awk` helper that lists object files needed by a kernel configuration.

Key responsibilities:
- Parses indented entries under `dev`, `misc`, `link`, and `ip` sections.
- Prefixes device entries as `dev<name>`.
- Adds non-option secondary tokens that do not begin with `+`, `=`, or `-`.
- Prints each discovered object as `<name>.$O`.

Role:
- Feeds mkfile dependency/object lists from the same kernel config grammar used by `mkdevc`.
