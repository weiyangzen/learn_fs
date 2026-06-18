# sources/user-network-fs/samba/source3/libsmb/libsmb_path.c

Purpose: implements URL encoding/decoding and parsing for libsmbclient `smb://` URLs. It turns user-facing SMB URLs into workgroup, server, port, share, path, user, password, and option components used by every file, directory, stat, and print operation.

Important APIs: internal `urldecode_talloc()` decodes `%xx` sequences into talloc output, stops at `%00`, and counts invalid escapes. `smbc_urldecode()` copies decoded output into a caller buffer. `smbc_urlencode()` percent-encodes characters outside the accepted unreserved set. `SMBC_parse_path()` parses `smb://[[[domain;]user[:password]@]server[:port][/share[/path]]][?options]`.

Control flow/state: parse initializes all output strings to safe defaults, inherits context port and workgroup, strips `?options`, handles empty root browsing, parses optional auth before the first slash, extracts numeric port, share, and backslash-normalized path, then URL-decodes path/server/share/user/password. It calls `smbc_set_credentials_with_fallback()` so DFS referral resolution has fresh credentials.

Dependencies and integration: relies on Samba string/token helpers, talloc, `hex_byte`, `nybble_to_hex_upper`, context getters, and credential update code in `libsmb_context.c`. Every URL-based operation depends on its output and error behavior.

Risks: malformed ports and non-`smb://` prefixes fail with `EINVAL` in callers. `%00` truncation can surprise callers but prevents embedded NUL propagation. Options are parsed but currently rejected by directory code if non-empty. IPv6 literal hosts with colons may be ambiguous because `:` is interpreted as port in server. Tests should cover root URLs, workgroup fallback, auth with domain/user/password, percent decoding including invalid and `%00`, port parse failures, slash-to-backslash conversion, and option extraction.
