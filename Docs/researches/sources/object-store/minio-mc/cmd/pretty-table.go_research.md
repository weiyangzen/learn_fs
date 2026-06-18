# Research: sources/object-store/minio-mc/cmd/pretty-table.go

## sources/object-store/minio-mc/cmd/pretty-table.go

Purpose: small colorized row formatter for fixed-width command output tables.

Important APIs and types: `Field` stores a color theme and maximum length; `PrettyTable` stores fields and separator; `newPrettyTable` constructs a table; `buildRow` renders a single row.

Control flow: `buildRow` iterates over the smaller of configured fields and provided contents. For fields with `maxLen >= 0`, it pads/truncates using `fmt` precision and manually replaces overlong content with a suffix of `...`; negative max length leaves content unchanged. Separators are inserted between rendered columns.

State and persistence: pure formatting helper with no persistent state.

Dependencies and integration: used by replication backlog and resync status output, and likely other CLI views. Depends on `console.Colorize`.

Risks and tests: truncation uses byte slicing and assumes `maxLen >= len("...")`; small max lengths can panic from negative slice bounds. Unicode display width is not handled. `pretty-table_test.go` covers basic ASCII behavior.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pretty-table.go -->
