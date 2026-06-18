# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/query.c

General-purpose ndb and connection-server query tool.

Key elements:
- Usage: `query [-acim] [-x netmtpt] [-f ndbfile] attr value [rattr]...`.
- Supports all matches (`-a`), connection server lookups (`-c`), IP info mode (`-i`), and multiple values (`-m`).
- Uses `ndbipinfo`/`csipinfo` in IP mode.
- Uses `ndbgetvalue`/`csgetvalue` for simple single-attribute lookups.
- Uses `ndbsearch` for broader database scans.
- Prints either bare values for single requested attributes or `attr=value` groups for multiple attributes.
- Installs `$` formatter for ndb values.

Notable behavior:
- `@` prefixes on requested attributes are ignored for matching via `skipat`.
- Connection-server mode is disabled when only `attr value` is provided.

Risks and quirks:
- Connection-server mode does not implement broad multi-result scanning without `ipinfo`.
