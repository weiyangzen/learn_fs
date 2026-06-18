# sources/user-network-fs/samba/source4/nbt_server/wins/winsserver.h

## Purpose

`winsserver.h` declares the WINS server runtime structure and the WACK/challenge IO contract used by WINS server and WREPL integration. It also includes generated `winsserver_proto.h` prototypes.

## Important APIs, Types, and Functions

`struct wins_server` holds the connected `winsdb_handle` and timing configuration for min/max renew interval, tombstone interval, and tombstone timeout. `struct wins_challenge_io` describes async name-query challenges to current owners: input server, NBT port, event context, name, and owner addresses; output address list returned by the challenged owner.

## Control Flow

The header has no executable flow. `winsserver.c` fills `wins_server` during nbtd startup and passes `wins_challenge_io` to `wins_challenge_send()` in `winswack.c`. WREPL IRPC proxy code also uses this IO model to request challenges through nbtd.

## State and Persistence Behavior

`wins_server` points at persistent WINS DB state through `wins_db` and holds in-memory configuration copied from loadparm. `wins_challenge_io` is request-scoped and talloc-owned by callers; outputs are stolen by receivers during `wins_challenge_recv()`.

## Dependencies and Integration Points

It depends on `winsdb_handle`, nbtd server declarations, tevent context, and NBT name structures. The generated prototype include connects server, client, WACK, and DNS proxy source files.

## Risks and Edge Cases

Because the config struct is simple public state, all users must agree on units and ownership. Challenge IO assumes `num_addresses` and `addresses` are consistent and non-empty; callers must validate before starting async work.

## Test Signals

Build signals include generated prototype correctness for `NBTD_WINS`. Runtime signals are WINS startup storing expected intervals and WACK challenge send/recv preserving address arrays across async callbacks.
