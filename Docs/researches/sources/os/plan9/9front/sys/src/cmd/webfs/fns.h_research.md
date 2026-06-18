# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/fns.h

Shared function declarations and format registrations for `webfs`.

Key contents:
- Memory/string/header helpers: `emalloc`, `estrdup`, `nstrcpy`, `addkey`, `delkey`, `getkey`, `lookkey`, `parsehdr`, `unquote`.
- URL formatting and parsing declarations with custom format verbs for escaped strings, IDN names, URLs, host bracket formatting, and encoded text.
- Bounded queue API: header/url metadata, read/write, close/free, allocation, 9p request attach, and flush.
- HTTP/authentication API: `authenticate`, `flushauth`, and `http`.

Notable dependencies:
- Must be included with `dat.h` so `Url`, `Key`, `Buq`, `Req`, and `Str2` are defined.

Research notes:
- The custom URL/header format verbs are installed by `webfs/fs.c` before mounting the service.
