# sources/user-network-fs/samba/source4/nbt_server/wins/wins_ldb.c

## Purpose

`wins_ldb.c` defines the `wins_ldb` LDB module used by `wins.ldb`. Its current role is to attach a `winsdb_handle` to the LDB context and provide a verification hook for WINS records before add/modify operations reach storage.

## Important APIs, Types, and Functions

The module entry point is `ldb_wins_ldb_module_init()`, which registers `ldb_wins_ldb_module_ops`. `wins_ldb_init()` creates a `struct winsdb_handle` with caller `WINSDB_HANDLE_CALLER_ADMIN` and a local owner address. `wins_ldb_verify()` intercepts `LDB_ADD` and `LDB_MODIFY`, retrieves the opaque `winsdb_handle`, skips special DNs, and dispatches based on `h->caller`.

## Control Flow

Initialization resolves `winsdb:local_owner` from loadparm; if absent, it loads interfaces and uses the first IPv4 address, falling back to `0.0.0.0`. It stores the handle as LDB opaque `winsdb_handle`. During add/modify, trusted callers `NBTD` and `WREPL` pass straight through; admin callers currently log a TODO warning and also pass through. Missing opaque state or unknown caller returns an LDB error.

## State and Persistence Behavior

The module stores a talloc-owned `winsdb_handle` in LDB opaque state. It does not directly persist WINS records, but it participates in every add/modify pipeline once listed in the `@MODULES` record of `wins.ldb`. The handle contains `local_owner`, caller identity, and the LDB context pointer.

## Dependencies and Integration Points

It depends on LDB module APIs, `winsdb.h`, Samba loadparm, interface discovery, and network helpers. `winsdb_connect()` ensures this module is present in `@MODULES` and reopens the database so the module is active.

## Risks and Edge Cases

Actual admin verification is still a TODO, so malformed admin writes may be accepted until lower layers detect corruption. If no loadparm opaque is present, `lpcfg_parm_string()` and interface loading assumptions can fail indirectly. The module trusts NBTD and WREPL callers, so their record construction invariants remain critical.

## Test Signals

Good tests include module initialization with explicit owner, interface-derived owner, and no-interface fallback; add/modify with each caller type; special DN bypass; missing opaque handle failure; and malformed admin records once verification is implemented.
