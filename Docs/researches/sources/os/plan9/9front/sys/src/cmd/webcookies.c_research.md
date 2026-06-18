# File Research: sources/os/plan9/9front/sys/src/cmd/webcookies.c

Cookie jar 9p filesystem used by `webfs` and other clients to share HTTP cookies. Conventionally mounted at `/mnt/webcookies`, it exposes an HTTP-oriented exchange file and a raw editable cookie file.

Key behavior:
- Maintains a `Jar` of `Cookie` entries with fields for name/value/domain/path/version/comment, expiration, secure flag, explicit domain/path flags, Netscape-style flag, deletion, marking, and on-disk state.
- Formats matching cookies as an HTTP `Cookie:` header and formats individual cookies as quoted attribute records for the persistent jar.
- Adds cookies by replacing same name/domain/path entries, sorts by name/domain and longer path first, purges deleted entries, expires session cookies on exit, and synchronizes to disk with a lock file.
- Parses persistent jar records through `addtojar()` and HTTP `Set-Cookie` headers through RFC2109 plus legacy Netscape parsing.
- Enforces domain/path/security checks before accepting response cookies or returning request cookies.
- `/http` protocol: first write must be an `http://` or `https://` URL; reads return matching `Cookie:` headers; later writes append response headers, parsed into the jar when the fid is destroyed.
- `/cookies` protocol: read/write raw cookie records, with `OTRUNC` replacing the jar on close.
- `main()` loads the jar from `-f` or `$home/lib/webcookies`, creates `http` and `cookies` files, and posts the service.

Notable dependencies:
- Plan 9 lib9p, Bio, ndb `ipattr`, time parsing, and quote formatting.

Research notes:
- Persistent jar synchronization uses `L.<file>` lock naming and retries before reporting lock acquisition failure.
- Header parsing mutates the input buffers in place.
- Raw cookie editing is bounded by `MaxCtext` to avoid unbounded memory growth.
