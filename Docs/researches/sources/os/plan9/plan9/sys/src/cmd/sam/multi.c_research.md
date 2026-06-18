# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/multi.c

Manages the host-side open-file list and menu ordering.

Key functions:
- `newfile` opens a `File`, assigns a monotonically increasing tag, inserts it into `file`, and notifies the terminal with `Hnewname`.
- `whichmenu` maps a `File*` to its menu index.
- `delfile` removes a file from the list, sends `Hdelname`, and closes storage.
- `fullname` and `fixname` canonicalize names relative to `curwd` and `cleanname`.
- `sortname` keeps the command file first, warns on duplicate names, and sends `Hmovname`.
- `state` changes clean/dirty/unread state and emits `Hclean`/`Hdirty`.
- `lookfile` finds a file by exact `String` name.

Behavior notes:
- File tags are protocol identifiers independent of menu order.
- Canonical display names are shortened relative to current working directory when possible.
