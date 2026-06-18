# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/btoken.h

This header declares internal support for PostScript Level 2 binary tokens and binary object sequences.

Key responsibilities:
- Defines access macros for system and user name tables:
  - `system_names_p`
  - `user_names_p`
- Declares `create_names_array`, used to create system or user name arrays in stable memory.
- Declares `encode_binary_token`, which serializes a Ghostscript `ref` object into binary object sequence representation.
- Defines `ref_binary_object_format` access through the interpreter context.

Dependencies and interfaces:
- Relies on implicit `i_ctx_p`, `gs_imemory`, `ref`, `gs_memory_t`, `client_name_t`, and `byte` types from Ghostscript interpreter internals.
- Comments warn that name table pointers may be `NULL`, so callers must check.

Notable implementation details:
- Header-only declarations/macros.
- No filesystem behavior or persistence logic.
- Important for binary PostScript/token support rather than image or file output.

Research classification: internal Ghostscript binary token support header.
