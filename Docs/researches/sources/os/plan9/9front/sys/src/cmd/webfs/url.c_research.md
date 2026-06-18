# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/url.c

URL parser, formatter, normalizer, matcher, and escaper for `webfs`.

Key behavior:
- Custom formatters emit percent-encoded strings, IDN/ascii domain names, bracketed IPv6-like hosts, and complete URLs.
- `url()` parses absolute and relative URLs against an optional base, splitting scheme/user/password/host/port/path/query/fragment.
- Relative URL paths are resolved through `abspath()` and `remdot()`, preserving directory semantics and removing dot components.
- Query `+` is decoded to space; host names are converted from IDN to UTF for internal use and to IDN during formatting.
- Percent decoding preserves reserved characters in path/query/fragment where required.
- `saneurl()` requires scheme, host, and path and strips default ports.
- `matchurl()` matches non-nil fields of a scope URL against a candidate URL, including path-prefix matching.
- `freeurl()` releases all URL components.

Notable dependencies:
- Plan 9 IDN helpers `utf2idn`/`idn2utf`, rune lowercasing, and custom `Fmt` verbs.

Research notes:
- `u->port` is lowercased like the host and scheme; numeric ports are unaffected.
- `saneurl()` treats a port string equal to the scheme as a default-port case.
