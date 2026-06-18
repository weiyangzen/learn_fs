# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/url.c

Implements Mothra URL fetching, posting, and resolving.

Key responsibilities:
- Supports `data:` URLs locally, decoding percent-encoded data or base64 payloads into an ORCLOSE temporary file.
- Supports `file:` URLs locally, resolving relative paths against a `file:` base, preserving fragment tags, cleaning paths, and opening the local file.
- Uses a web file service mounted at `mtpt` (`/mnt/web` by default) for network-style URLs.
- `webclone` opens `/mnt/web/clone`, writes `baseurl` and `url` controls, and returns the connection path.
- `urlpost` opens a connection, optionally sets content type, and returns a writable `postbody`.
- `urlget` fetches local/data URLs first, otherwise uses `/mnt/web/<conn>/body` or `errorbody`, reads parsed URL/fragment/content type/content encoding, and pipes compressed bodies through `uncompress`, `gunzip`, or `bunzip2`.
- `urlresolve` asks `/mnt/web` for parsed absolute URL and fragment without reading the body.

Important interactions:
- Used by Mothra UI/link code and the form/posting path.
- Relies on `pipeline` from `mothra.c` for content decoding filters.
- Shares the mutable `Url` structure fields declared in `mothra.h`.

Notable quirks:
- The network implementation is delegated entirely to the mounted web file system.
- `fileget` temporarily edits strings while resolving path components and then restores them.
