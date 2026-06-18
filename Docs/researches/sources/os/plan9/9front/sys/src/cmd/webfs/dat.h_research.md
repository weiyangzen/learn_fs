# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/dat.h

Shared data definitions for `webfs`.

Key contents:
- Declares `Url`, `Buq`, `Buf`, `Key`, and `Str2`.
- `Url` splits scheme, user, password, host, port, path, query, and fragment.
- `Buf` is an internal queued data chunk with read/end pointers and optional blocked write request.
- `Key` is a linked header key/value record with inline key storage and value pointer.
- `Buq` is a reference-counted, qlocked bounded stream with URL/header metadata, close/error state, queued buffers, queued 9p reads, and rendezvous.
- Defines global `debug`, `proxy`, `timeout`, and `whitespace`, plus `Domlen`.

Notable dependencies:
- Uses lib9p `Req`, Plan 9 `Ref`, `QLock`, and `Rendez`.

Research notes:
- The header is intentionally compact and is paired with function declarations in `fns.h`.
