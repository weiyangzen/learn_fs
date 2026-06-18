# File Research: sources/os/bsd/freebsd-src/sbin/hastd/token.l

`token.l` is the flex lexer for HAST configuration parsing. It emits parser tokens for top-level config keywords, replication/checksum/compression values, boolean-like tokens, resource fields, numbers, strings, and braces.

It tracks global `depth` on `{`/`}` and global `lineno` on newlines. Numeric tokens use `atoi()`, string tokens are duplicated with `strdup()`, comments beginning with `#` and whitespace are ignored, and legal string characters are alphanumerics plus `.`, `-`, `_`, `/`, `:`, `[`, and `]`.
