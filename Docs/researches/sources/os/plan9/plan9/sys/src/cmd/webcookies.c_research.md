# File Research: sources/os/plan9/plan9/sys/src/cmd/webcookies.c

This standalone cookie filesystem lets clients such as `hget` and multiple `webfs` instances collaborate through a shared persistent cookie jar. It mounts conventionally at `/mnt/webcookies`.

Filesystem surface:
- `http`: clients write a URL first, read generated outgoing `Cookie:` headers, then write response headers so `Set-Cookie` values can be stored.
- `cookies`: editable textual view of the full cookie jar.

Cookie model:
- `Cookie` stores name/value, domain, path, version, comment, expiration, secure flag, explicit-domain/path flags, Netscape-style marker, and internal deleted/mark/ondisk flags.
- `Jar` stores dynamic cookie array, file qid/dirty state, jar file path, and lock file path.

Formatting:
- `%J` emits HTTP `Cookie:` header format.
- `%K` emits the editable/persistent cookie line format with quoted string fields and integer flags.

Jar management:
- `addcookie` replaces cookies with matching name/domain/path unless exact match already exists.
- `purgejar` compacts deleted cookies.
- `syncjar` locks with `L.<filename>`, merges disk state, removes marked entries, writes non-session cookies back, and updates qid.
- `readjar` derives lockfile name and loads the jar.
- `closejar` expires cookies and syncs.

Matching and validation:
- `isdomainmatch` implements RFC2109-style host/domain matching.
- `iscookiematch` checks domain, path prefix, and expiration.
- `cookiesearch` builds a sorted subjar for outgoing cookies, respecting `secure`.
- `isbadcookie` rejects invalid Set-Cookie domains/paths.

HTTP Set-Cookie parsing:
- Handles RFC-style and old Netscape-style cookies.
- Netscape detection looks for no spaces around `=`, no quotes, no Version attribute.
- `strtotime` parses GMT expiration date variants.
- `parsehttp` scans response headers for `Set-Cookie:` and calls `parsecookie`.
- `parsecookie` parses NAME=VALUE plus domain/path/comment/version/expires/max-age/secure attributes; missing domain/path default to the request host/path-derived directory.

9P request handling:
- `fsopen` creates per-fid `Aux` state for `http` or `cookies`.
- `fswrite` on `http` either captures URL/domain/path and computes outgoing cookies or appends response headers.
- `fsread` on `http` returns outgoing header text after URL has been written.
- `fsdestroyfid` parses accumulated response headers or applies edited cookie text, then syncs jar.
- `main` installs formatters, creates default `$home/lib/webcookies` if needed, builds a static tree with `http` and `cookies`, and posts the server.

Notable risks and differences from `webfs/cookies.c`:
- This version's `isdomainmatch` is stricter than `webfs/cookies.c`; it does not accept a bare `google.com` for `.google.com`.
- Cookie/header buffers for `http` are fixed at 4096 bytes.
- Secure/certificate concerns are outside this file; it trusts callers to identify `https://` correctly.
