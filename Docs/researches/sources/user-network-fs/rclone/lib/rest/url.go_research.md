# sources/user-network-fs/rclone/lib/rest/url.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/url.go -->
## sources/user-network-fs/rclone/lib/rest/url.go

Purpose: provides URL path helpers for joining escaped paths and applying stricter percent encoding.

Important APIs and control flow: `URLJoin(base, path)` parses `path` as a URL reference and resolves it against `base`, returning parse errors with context. `URLPathEscape(in)` uses `url.URL{Path: in}.String()` to escape path content while preserving path semantics. `URLPathEscapeAll(in)` iterates bytes and percent-encodes every byte except RFC 3986 unreserved characters and `/`.

State, dependencies, and integration: stateless helpers depending on `net/url`, `fmt`, and `strings`. They integrate with REST backends constructing object URLs where path escaping rules vary.

Risks and test signals: `URLJoin` treats absolute URLs and absolute paths according to normal URL resolution, which can replace base paths. `URLPathEscape` has Go URL quirks such as colon handling; `URLPathEscapeAll` operates on UTF-8 bytes, producing percent-encoded UTF-8 for non-ASCII. Tests cover join cases, colon/percent/space escaping, and stricter all-character escaping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/rest/url.go -->
