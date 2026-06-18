# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_alias.py

## Purpose
Tests alias creation and listing through the CLI, with emphasis on command-line and stdio encoding behavior.

## Important APIs, Types, And Functions
`ListAlias` combines `GridTestMixin`, `CLITestMixin`, and Trial `TestCase`. `_check_create_alias(alias, encoding)` is the shared Deferred-based scenario for `create-alias` and `list-aliases --json`. Test methods cover no declared encoding, ASCII, and UTF-8 with a non-ASCII alias.

## Control Flow
Each scenario creates a one-share grid, monkey-patches `encodingutil.io_encoding`, runs `create-alias`, verifies stdout/stderr/return code, reads aliases from the client directory, then runs `list-aliases --json` and checks readwrite/readonly fields in decoded JSON.

## State And Persistence
The tests persist aliases in the generated client node directory. No external state is modified beyond the temporary grid.

## Dependencies And Integration Points
Depends on CLI common helpers, `get_aliases()`, no-network grid setup, Twisted Deferreds, JSON parsing, and Tahoe encoding utilities.

## Risks And Test Signals
The central risk is Unicode handling drifting between Python strings, argv encoding, filesystem alias storage, and JSON output. Test signals are exact `Alias '<name>' created` output, zero stderr, `URI:DIR2:` readwrite alias storage, JSON keys preserving the alias, and successful snowman alias handling under UTF-8.
