# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_query.c

## Role

Implements `-Q/--query <query-format>`, a read-only formatted metadata query facility for `tunefs.ocfs2`.

## Format Specifiers

The operation registers custom GNU printf handlers:

- `%B`: block size
- `%T`: cluster size
- `%N`: number of node slots
- `%R`: root directory block
- `%Y`: system directory block
- `%P`: first cluster group block
- `%V`: volume label
- `%U`: UUID string
- `%M`: compat feature flags
- `%H`: incompat feature flags plus tunefs in-progress flags
- `%O`: read-only compatible feature flags

It rejects standard printf specifiers during parse via `parse_printf_format()` so only custom query specifiers are allowed.

## Run Flow

`query_parse_option()` stores the format string in `op->to_private`.

`process_escapes()` converts C-style escapes such as `\n`, `\t`, `\r`, and `\a`.

`query_run()` registers custom printf handlers, sets global `query_fs`, prints the processed format string to stdout, then clears the global and frees the processed string.

## Dependencies

Uses GNU extensions: `_GNU_SOURCE`, `asprintf()`, `register_printf_function()`, and `parse_printf_format()`.

## Safety Model

This is declared `TUNEFS_FLAG_RO` and does not modify metadata.

## Notable Risks

- Uses a global `query_fs` to pass filesystem context into printf handlers. That is fine for a CLI but not thread-safe or reentrant.
- `fprintf(stdout, fmt)` intentionally treats user input as a format string after custom validation. The validation is important; any missed standard specifier could become a format-string issue.
- `register_printf_function()` is a GNU libc extension and deprecated in newer glibc contexts, limiting portability.
