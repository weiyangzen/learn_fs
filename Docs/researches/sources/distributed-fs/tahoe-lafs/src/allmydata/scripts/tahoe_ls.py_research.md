# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_ls.py

## Purpose
Implements `tahoe ls`, listing directory children or a single file node from Tahoe webapi JSON with optional JSON passthrough, long format, classification suffixes, and URI display.

## Important APIs, Types, and Functions
The public API is `ls(options)`. It resolves aliases, calls `GET /uri/<cap>/<path>?t=json`, optionally prints raw JSON, otherwise parses the node tuple and formats rows using metadata, readonly/write caps, file sizes, and terminal-safe output helpers.

## Control Flow
The command normalizes node URL and trailing slash input, handles 404 as exit code 2 and connection status 0 as exit code 3, parses webapi JSON, derives `children` from either a dirnode or a single node, computes row widths, and prints rows to stdout unless Unicode encoding fails, in which case it prints escaped names to stderr and returns 1.

## State and Persistence Behavior
No persistent writes. It reads remote node metadata and uses current wall clock time to choose GNU-ls-like date formatting for link creation/modification times.

## Dependencies and Integration Points
Depends on `common.get_alias`, `escape_path`, `common_http.do_http`, `encodingutil` conversions, and Tahoe webapi JSON node format. It uses `six.ensure_text` to normalize URI cells.

## Risks and Edge Cases
Unknown child node types are listed with `?` and trigger a warning. Metadata assumptions can fail if webapi payloads omit expected `metadata`. Raw JSON mode rejects unprintable non-ASCII bytes even though webapi should return printable ASCII. Long output width computation is display-width naive for complex Unicode.

## Test Signals
`test_cli.py` covers help, list behavior, empty directories, Unicode listing behavior via `test_cp.py`, missing aliases, and JSON/formatting paths indirectly through grid CLI integration.
