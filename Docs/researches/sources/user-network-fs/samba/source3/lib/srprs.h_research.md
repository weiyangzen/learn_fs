## sources/user-network-fs/samba/source3/lib/srprs.h

Purpose: public interface and contract documentation for the simple recursive parser implemented in `srprs.c`. It forward-declares `struct cbuf` and exposes cursor-based matching functions that are composable in larger parsers.

Important APIs are the whitespace, character, string, charset, quoted-string, hex, newline, end-of-string, line, and quoted escaped-string matchers. The documentation states the key semantic guarantee: functions update the parse position and output only if they match, otherwise they leave arguments unchanged, with `cbuf` rollback guaranteed up to the current write position.

Control flow is not in the header, but its comments describe parser composition: callers pass `const char **ptr`, inspect boolean returns, and may use a `cbuf` for accumulated output. The continuation example for `srprs_quoted_string` is especially important because it documents multi-call parsing where an unterminated quote can be accepted temporarily when `cont` is supplied.

State and persistence: the header declares no storage. Parser state is held by caller variables. Dependencies are only C/Samba base types and `struct cbuf` at compile time.

Risks: the API relies on callers understanding pointer ownership and null-terminated input; it has no length-bounded variants. The comments say `srprs_hex` matches a hex string of maximum length, while many callers might expect exactly that length. Test signals for consumers should verify they do not assume destructive parsing on failure and that they handle `NULL` output buffers only for functions whose docs allow it.
