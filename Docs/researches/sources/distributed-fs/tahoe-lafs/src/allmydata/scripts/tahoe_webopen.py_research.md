# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_webopen.py

## Purpose
Implements `tahoe webopen`, opening the node web UI or a specific Tahoe object/path in a browser.

## Important APIs, Types, and Functions
The public function is `webopen(options, opener=None)`. It resolves optional `where`, constructs a web URL, optionally appends `?t=info`, and calls an injectable opener for testability.

## Control Flow
If no target is supplied, the node URL is opened. Otherwise the command resolves aliases, treats path `/` as empty, builds `/uri/<rootcap>/<escaped-path>`, appends info query if requested, and opens the URL. Alias errors return 1.

## State and Persistence Behavior
No local or remote persistence; this is a URL construction and browser-dispatch helper.

## Dependencies and Integration Points
Depends on `common.get_alias`, `escape_path`, and `urllib.parse.url_quote`. Integrates with the host browser through the opener callback or default webbrowser behavior supplied by the caller.

## Risks and Edge Cases
Opening writecaps in a browser may expose sensitive caps to browser history/logs. URL construction must preserve Tahoe path escaping. Behavior for absent opener depends on runner wiring not shown in this file.

## Test Signals
`test_cli.py` covers webopen help, nonexistent alias handling, and URL construction/opening behavior with a fake opener.
