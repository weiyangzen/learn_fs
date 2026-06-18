# Research: sources/object-store/minio-mc/cmd/pretty-record.go

## sources/object-store/minio-mc/cmd/pretty-record.go

Purpose: small formatter for colorized multi-line key/value records with a heading row and aligned subsequent rows.

Important APIs and types: `Row` stores a description and color theme; `PrettyRecord` stores row config, indent, and max description length; `newPrettyRecord` computes alignment; `buildRecord` renders supplied content.

Control flow: `buildRecord` uses the smaller of configured row count and content count. The first row is rendered as a heading with no key label. Later rows use the configured indent and max label width, then colorize the full formatted line per row theme.

State and persistence: no state outside returned structs and strings.

Dependencies and integration: uses `console.Colorize`; likely shared by command output formatters outside this subset.

Risks and tests: alignment uses byte length rather than display width, so wide Unicode and ANSI color content can misalign. There are no direct tests for `PrettyRecord`.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pretty-record.go -->
