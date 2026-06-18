# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/btoken.h

This header defines support interfaces for PostScript Level 2 binary tokens.

Key contents:
- Macros for accessing system and user name arrays through the current interpreter context and memory spaces.
- Declaration for `create_names_array`, which creates stable-memory name tables.
- Declaration for `encode_binary_token`, converting a Ghostscript object ref into binary object sequence representation.
- Macros exposing `binary_object_format` as a managed ref inside `i_ctx_p`, so save/restore can handle it correctly.

This is parser/interpreter state infrastructure. It has no filesystem logic.
