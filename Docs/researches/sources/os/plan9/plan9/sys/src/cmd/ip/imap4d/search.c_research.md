# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/search.c

Implements IMAP `SEARCH` predicate evaluation over parsed `Msg` structures.

Key behavior:
- `searchMsg` ensures `msgStruct(m, 1)` is available, then evaluates a linked list of `Search` predicates with AND semantics.
- Supports boolean operators `NOT` and `OR`, flag predicates, keyword masks, size predicates, address fields, subject, internal/sent dates, UID/sequence sets, header search, body search, and text search.
- `fileSearch` streams a message file with overlap equal to pattern length so matches spanning read boundaries are found.
- `headerSearch` uses `selectFields` to isolate a named header and searches only the value region after `:`.
- `addrSearch` converts `MAddr` entries to strings and performs case-insensitive substring search.
- `dateCmp` compares only year/month/day from parsed dates.

Integration points:
- Relies on `msgStruct`, `msgSize`, `msgFile`, `selectFields`, `maddrStr`, and flag/date fields populated by `msg.c`.
- Search AST types and constants come from the IMAP parser definitions in `imap4d.h`.

Risks and notes:
- Comments note header/envelope searches should decode MIME charset escapes, but this implementation does not.
- `dateCmp` assumes `date2tm` yields meaningful fields; invalid dates are not explicitly rejected here.
