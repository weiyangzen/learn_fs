## sources/test-tools/syzkaller/pkg/kconfig/parser.go

Purpose: low-level line parser for Kconfig syntax.

Important APIs/types/functions: `parser`, `newParser`, `nextLine`, `readNextLine`, `skipSpaces`, `identLevel`, `failf`, `eol`, `char`, `peek`, `ConsumeLine`, `TryConsume`, `MustConsume`, `QuotedString`, `TryQuotedString`, `Ident`, and `Shell`.

Control flow: `nextLine` enforces that previous lines were fully consumed and joins backslash-continuations. Token helpers advance `col`, skip spaces, and set the first parse error. Quoted strings support simple escapes and embedded shell expressions; `Shell` tracks nested parentheses and quoted strings.

State and persistence: parser mutates its byte buffer, current line, line/column, and error field.

Dependencies and integration: used by `expr.go` and `kconfig.go`.

Risks: parser is purpose-built and not a full Kconfig grammar. Error recovery stops at first error. `TryConsume` is prefix-based and must be ordered carefully by callers for operators like `!=` and `!`.

Test signals: indirectly covered by expression and Kconfig tests/fuzzing.
