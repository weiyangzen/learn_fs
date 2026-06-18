<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/interact.c -->
# sources/user-network-fs/samba/source3/utils/interact.c

## Purpose
`interact.c` provides small user-interaction helpers for Samba command-line tools: single-character prompts and edit-in-external-editor workflows.

## Important APIs, types, and functions
- `get_editor()` chooses `$VISUAL`, then `$EDITOR`, then `vi`, caching the result in a static 64-byte buffer.
- `interact_prompt()` disables canonical input and echo, prompts until the user enters an accepted character or newline for the default, restores terminal settings, and returns the character or EOF.
- `interact_edit()` writes an initial string to a secure temporary file, runs the selected editor on it, reads the edited content into a talloc string, unlinks the file, and returns it.

## Control flow
`interact_prompt()` temporarily changes terminal flags with `tcgetattr`/`tcsetattr`, loops with `getchar()`, validates against a lowercase accept string, and restores flags before returning. `interact_edit()` creates `/tmp/net_idmap_check.XXXXXX` with group/other permissions masked off, writes the initial string, launches `system("<editor> <file>\n")`, reads the file back in 128-byte chunks, and steals the result onto the caller's talloc context.

## State and persistence behavior
The editor helper creates a temporary file and unlinks it after reading or on most error paths. The chosen editor is cached in process-static memory. No persistent application state is written unless the external editor or environment causes side effects.

## Dependencies and integration points
The file uses Samba `d_printf`/`DEBUG`, talloc string append/steal, POSIX termios, `mkstemp`, stdio, `system()`, and environment variables. It is declared by `interact.h` and used by interactive `net` subcommands.

## Risks and edge cases
- `system()` builds a shell command from the editor string and temp path, so unusual editor values can invoke shell metacharacters.
- `interact_prompt()` does not check terminal API failures and may misbehave on non-TTY stdin.
- `tolower(c)` should be used carefully for EOF and locale behavior.
- The temporary filename is hard-coded under `/tmp` and named for net idmap.

## Test signals
Manual tests can verify default selection, accepted-character filtering, terminal restoration after invalid input, editor selection through environment variables, and cleanup of temp files. Automated tests should mock stdin/editor behavior where possible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/interact.c -->
