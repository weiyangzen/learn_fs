# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnsquery.c

Interactive client for the mounted `/net/dns` 9P DNS service.

Key elements:
- Opens `/net/dns` by default, `/net.alt/dns` with `-x`, or a provided path.
- Prompts for query lines, trims whitespace, and writes each query to the DNS file.
- Defaults to `ip` query for names and `ptr` query for IP literals.
- Converts PTR inputs to reverse names with `mkptrname`.
- Preserves leading `!` to request attribute-value output from `dns.c`.
- Reads and prints all returned data after each query.

Notable behavior:
- Uses the existing mounted DNS service rather than linking resolver internals.
- Prints write errors as `!%r`.

Risks and quirks:
- Minimal parsing; queries with spaces are passed through as-is.
