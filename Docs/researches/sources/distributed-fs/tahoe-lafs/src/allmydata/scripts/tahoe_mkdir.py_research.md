# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_mkdir.py

## Purpose
Implements `tahoe mkdir`, creating an unlinked Tahoe directory or a linked child directory at a path.

## Important APIs, Types, and Functions
The public function `mkdir(options)` resolves aliases and issues `POST ?t=mkdir`. It uses `check_http_error()` for response handling and prints the returned directory writecap with `quote_output()`.

## Control Flow
If no target or no path is supplied, it posts to `/uri?t=mkdir`, optionally adding `format=...`. Otherwise it resolves the alias/path, strips a trailing slash, posts to `/uri/<rootcap>/<path>?t=mkdir`, optionally appending format, prints the new URI, and returns 0 unless early alias or HTTP errors occur.

## State and Persistence Behavior
All persistent state is remote Tahoe directory creation/link mutation through the webapi. No local files are changed.

## Dependencies and Integration Points
Depends on `common.get_alias`, `common_http.do_http/check_http_error`, and webapi mkdir semantics. It integrates with CLI options for mutable directory format selection.

## Risks and Edge Cases
The linked-path URL uses `url_quote(path)` rather than `escape_path(path)`, which may encode slashes differently than other modules; this appears intentional/legacy but is a path-handling risk. It calls `check_http_error()` for linked mkdir but does not return early on nonzero status before reading/printing the body.

## Test Signals
`test_cli.py` covers mkdir help, normal mkdir, mutable type selection, unlinked mutable creation, bad mutable type, Unicode path creation, and missing/nonexistent aliases.
