# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/url.c

This file is the regex-driven URL parser and URL utility library for `webfs`. It targets RFC1738/RFC2396 common internet schemes with some RFC2732 IPv6 literal support.

Supported schemes:
- Known: `http`, `https`, `ftp`, `file`.
- Unknown schemes are preserved as scheme data but not opened.
- Relative URLs are resolved against a base URL.

Regex table:
- Splits scheme, authority, path, query, and fragment.
- Validates scheme, authority, host, userinfo, absolute path, query, fragment, HTTP path, FTP path, and file path.
- `initurl` compiles regexes and validates submatch indices.

Relative resolution:
- `merge_relative_path` implements RFC2396 section 5.2 path merging and dot-segment removal.
- `resolve_relative` inherits base scheme/authority/path/query/fragment as appropriate and can expand current-document references.

Parsing pipeline:
- `parseurl` duplicates input, splits it, resolves relative references if needed, parses scheme/fragment, handles unknown schemes, parses query/authority/path, and runs scheme-specific postparse.
- `postparse_http` sets open/read/close callbacks, validates authority/host, and builds `http.page_spec`.
- `postparse_ftp` validates FTP authority/path, rejects query and unexpected params, and extracts `;type=`.
- `postparse_file` rejects user/pass/query/port, requires path, and normalizes `localhost`.

Utilities:
- `freeurl` frees all fields and scheme-specific allocations.
- `rewriteurl` reconstructs `u->url` from parsed fields.
- `seturlquery` validates and replaces query.
- `copyurl` deep-copies parsed URL state.
- `escapeurl` percent-encodes bytes selected by caller.
- `unescapeurl` decodes percent escapes to Latin-1 runes.

Notable implementation issues:
- `parse_userinfo` assigns both user and password submatches to `u->user`; the password branch should likely assign `u->passwd`.
- In `resolve_relative`, the fragment-copy branch uses `su->query.s` while appending fragment bytes, which appears wrong and can copy from the wrong component.
- `unescapeurl` checks `r[0]=='0' && r[2]=='0'` after advancing past `%`; the second hex digit is `r[1]`, so escaped-NUL detection appears off.
