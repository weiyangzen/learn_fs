## sources/sync-backup/bup/lib/bup/url.py

Purpose: byte-preserving parsing and rendering of Bup path URLs, especially file/ssh-style URLs where command-line paths must not be decoded accidentally.

Important APIs and control flow: `URL` is a frozen dataclass with scheme, host, port, user, and path. `parse_bytes_path_url()` parses RFC-3986-like URLs, percent-decodes user/host but leaves path bytes untouched, handles IPv4/IPv6 literals, drops passwords, and returns either `None`, a `URL`, or an error string. `render_url()` percent-encodes user/host, handles IPv6 brackets, and can dot-encode relative paths under authorities via `dot_encode_path()`.

State and dependencies: stateless; depends on `ipaddress`, `urllib.parse.unquote_to_bytes`, regexes, and `path_msg()` for diagnostics. Integration points are remote repo/config parsing and command-line source/destination handling.

Risks and tests: path bytes are intentionally not percent-decoded, so callers must choose this parser only where that behavior is desired. `port=0` is not rendered because `if self.port` treats zero as absent. Invalid host handling is regex based after IP checks. Direct URL tests are outside this subset, while import and remote init/save scenarios exercise URL-like `-:repo` paths.
