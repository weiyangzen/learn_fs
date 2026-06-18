# File Research: sources/local-fs/xfsdump/invutil/stobj.h

Declares storage-object interactive menu APIs.

Exports:
- menu generation and file lifecycle: `generate_stobj_menu`, `open_stobj`, `close_stobj_file`, `close_all_stobj`.
- highlight handlers for sessions, streams, and media files.
- select, commit, prune, undelete, and delete callbacks.

Role:
- Connects storage-object-specific menu operations to the generic `cmenu` and `list` infrastructure.
