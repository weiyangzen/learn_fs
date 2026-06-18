<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/interact.h -->
# sources/user-network-fs/samba/source3/utils/interact.h

## Purpose
`interact.h` declares interactive helper functions for Samba utilities.

## Important APIs, types, and functions
- `interact_edit(TALLOC_CTX *mem_ctx, const char *str)` opens an external editor on initial text and returns edited content allocated under `mem_ctx`.
- `interact_prompt(const char *msg, const char *accept, char def)` asks for one accepted character with a default.

## Control flow
No control flow is implemented in the header. It defines a small API for command modules that need human confirmation or text editing.

## State and persistence behavior
The header implies returned memory ownership through talloc. Runtime state and temporary-file behavior live in `interact.c`.

## Dependencies and integration points
It includes talloc and is consumed by utility modules such as net/idmap tooling that need interactive edits or prompts.

## Risks and edge cases
- Callers must handle `NULL` from `interact_edit()` and EOF or unexpected return values from `interact_prompt()`.
- The API assumes synchronous terminal/editor interaction.

## Test signals
Compile coverage and command-level interactive tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/interact.h -->
