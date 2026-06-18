# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_invite.py

## Purpose
Implements the `tahoe invite` subcommand, creating a Magic Wormhole exchange that sends introducer and share-configuration data to a new client node.

## Important APIs, Types, and Functions
`InviteOptions` parses a single nickname plus optional share parameters. `_send_config_via_wormhole(options, config)` performs the server-side wormhole protocol. `invite(options)` reads the local node config, derives the introducer FURL, builds the remote config, and sends it. `subCommands` and `dispatch` register the command.

## Control Flow
`invite()` chooses a basedir from the global node directory or default, reads `tahoe.cfg`, obtains the introducer FURL, and fills missing share values from the `[client]` config. `_send_config_via_wormhole()` connects to the configured wormhole relay/appid, allocates and prints an invite code, sends server abilities, waits for a client intro, verifies `client-v1`, sends JSON config, and closes.

## State and Persistence Behavior
This module does not write local state. It reads node config and transmits a JSON config over the wormhole. The visible invite code is transient and printed to stdout.

## Dependencies and Integration Points
Uses Twisted `inlineCallbacks`, global runner-provided wormhole settings, `read_config()`, `get_introducer_furl()`, and `jsonbytes`. It integrates with `create-node --join` on the receiving side and with Magic Wormhole relay/application IDs.

## Risks and Edge Cases
Protocol negotiation is strict: missing `abilities` or `client-v1` returns 1 from the helper. Missing introducer FURL raises `SystemExit(1)`. Share options are strings from CLI/config, so downstream consumers must tolerate string numeric values. The helper imports the global `reactor`, which makes isolation/testing more delicate.

## Test Signals
`src/allmydata/test/cli/test_invite.py` covers successful invites, share config fallback, missing FURL, wrong/missing client/server abilities, missing nickname, illegal create-node join options, and create-node join integration.
