# File Research: sources/teaching/xv6-public/mkdir.c

User-space directory creation utility.

Behavior:
- Requires one or more path arguments.
- Calls `mkdir` for each path.
- Stops after the first failed creation and prints a diagnostic.
