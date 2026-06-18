# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/csquery.c

Small client for querying `/net/cs`.

Behavior:
- Usage: `ndb/csquery [/net/cs [addr...]]`.
- Optional `-s` status-only mode suppresses normal output and only records errors.
- Opens the selected connection server file, writes the query string, then seeks back and reads all translated replies.
- With address arguments, queries each argument and exits with error status if any translation failed.
- With no query arguments, enters an interactive loop reading lines from stdin after printing `> ` prompts.

Important interactions:
- Talks directly to the 9P `cs` file implemented by `ndb/cs`.
- Uses simple read/write protocol rather than linking to resolver internals.
