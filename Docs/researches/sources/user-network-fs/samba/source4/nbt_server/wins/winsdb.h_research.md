# sources/user-network-fs/samba/source4/nbt_server/wins/winsdb.h

## Purpose

`winsdb.h` defines the public data structures, flags, caller identities, hook actions, and generated prototypes for Samba's WINS database layer. It is the shared contract between nbtd WINS server/client code, WREPL paths, the LDB module, and hook integration.

## Important APIs, Types, and Functions

Important types are `struct winsdb_addr`, `struct winsdb_record`, `enum winsdb_handle_caller`, `struct winsdb_handle`, and `enum wins_hook_action`. Flags `WINSDB_FLAG_ALLOC_VERSION` and `WINSDB_FLAG_TAKE_OWNERSHIP` control write behavior. The header includes `winsdb_proto.h`, which provides prototypes for the implementation functions in `winsdb.c` and `wins_hook.c`.

## Control Flow

The header has no executable control flow, but it defines how callers construct records before database writes: fill a `winsdb_record`, pass ownership/version flags, and let the implementation allocate version IDs or local owner when needed. Caller identity on `winsdb_handle` feeds into the `wins_ldb` module verification path.

## State and Persistence Behavior

`struct winsdb_record` mirrors persistent LDB WINS records: name, WREPL type/state/node, static bit, expiration, version, owner, registered-by debug field, and a NULL-terminated list of `winsdb_addr` entries. `struct winsdb_handle` carries the persistent LDB context, caller class, local owner address, and hook script path.

## Dependencies and Integration Points

It relies on NBT and WREPL generated types already included by users, LDB forward declarations, tevent forward declarations, and source4 nbtd code. It is included by WINS DB implementation, server logic, WACK logic, DNS proxy, and the LDB module.

## Risks and Edge Cases

The header exposes raw struct fields rather than opaque accessors, so callers must maintain invariants such as NULL-terminated address lists, valid WREPL state/type combinations, address count limits, and correct talloc ownership. The caller enum is security-relevant because module verification policy changes based on it.

## Test Signals

Compile-time signals are generated prototype freshness and all WINS users building against the same structure definitions. Runtime tests should validate that records assembled by nbtd and WREPL satisfy the invariants consumed by `winsdb_message()` and `winsdb_record()`.
