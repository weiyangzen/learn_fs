# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_unlink.py

## Purpose
Implements `tahoe unlink`/delete-like removal of a directory entry from a Tahoe directory.

## Important APIs, Types, and Functions
The command function is `unlink(options, command="unlink")`. It resolves aliases, requires a non-empty path, constructs `/uri/<rootcap>/<path>`, sends `DELETE`, and prints formatted success or error messages.

## Control Flow
After node URL normalization and alias resolution, the command rejects attempts to unlink an alias root without a child path. It sends one DELETE request and returns 0 only for HTTP 200.

## State and Persistence Behavior
All persistence is remote Tahoe directory entry removal. The target object may remain reachable by other caps/links; this command only removes the named link.

## Dependencies and Integration Points
Depends on `common.get_alias`, `escape_path`, `common_http.do_http`, and webapi DELETE semantics.

## Risks and Edge Cases
It cannot remove alias roots. It treats only status 200 as success, so alternate no-content delete responses would be reported as failures. As with other path commands, behavior depends on precise alias/path escaping.

## Test Signals
`test_cli.py` covers unlink help, missing default alias, nonexistent alias, missing path, and normal unlink behavior through CLI integration.
