# File Research: sources/os/plan9/plan9/sys/src/9/port/mkextract

Purpose: rc helper for extracting a numbered field from a named section in one or more config files.

Key logic:
- Usage: `mkextract [-u] field n file...`.
- Finds indented lines under a top-level section named by `field`.
- Prints field `n` from those lines.
- With `-u`, sorts uniquely.

Dependencies and integration:
- Uses `rc`, `awk`, `sort`, and kernel config indentation rules.
