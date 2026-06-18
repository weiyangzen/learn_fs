# sources/user-network-fs/samba/source4/nbt_server/wins/winsdb.c

## Purpose

`winsdb.c` is the core WINS database access layer for Samba's source4 nbtd and WREPL paths. It maps NetBIOS names to LDB DNs, decodes and encodes WINS record attributes, manages version allocation, updates address lists, applies expiration semantics, and performs transactional add, modify, delete, and connect operations for `wins.ldb`.

## Important APIs, Types, and Functions

Public APIs include `winsdb_connect()`, `winsdb_get_maxVersion()`, `winsdb_set_maxVersion()`, `winsdb_lookup()`, `winsdb_record()`, `winsdb_add()`, `winsdb_modify()`, `winsdb_delete()`, and address-list helpers `winsdb_addr_list_make()`, `winsdb_addr_list_add()`, `winsdb_addr_list_remove()`, `winsdb_addr_list_check()`, `winsdb_addr_list_length()`, and `winsdb_addr_string_list()`. Important internals are `winsdb_dn()`, `winsdb_nbt_name()`, `winsdb_addr_decode()`, `ldb_msg_add_winsdb_addr()`, `winsdb_message()`, and `winsdb_check_or_add_module_list()`.

## Control Flow

Lookup computes an LDB DN from the `nbt_name`, searches the base DN, and converts the returned message with `winsdb_record()`. Record decoding reconstructs the name from DN components, validates name/scope length, reads record metadata, decodes each `address` value, filters locally owned expired active addresses, and releases active records with no remaining active addresses. Add and modify start LDB transactions, optionally allocate a new version with `winsdb_set_maxVersion(h, 0)`, optionally take ownership, encode the record to an LDB message, and commit. Delete removes the DN in a transaction. After successful commits, WINS hooks are called.

## State and Persistence Behavior

Persistent state is stored in `wins.ldb` under DNs composed from scope, name, and type. `CN=VERSION` stores `maxVersion`; `@MODULES` stores the `wins_ldb` module list. Dynamic addresses are stored as strings containing address, owner, and expire time, while static records store only the address string and receive maximum expiration during decode. Transactions protect version and record updates, although `winsdb_set_maxVersion()` starts its own transaction and is called inside add/modify transactions.

## Dependencies and Integration Points

The file depends on LDB, LDB wrap, generated NBT/WREPL enums, talloc, loadparm, interface discovery, time helpers, string conversion helpers, and talloc-aware sorting. It is used by `winsserver.c`, WREPL code, the `wins_ldb` module, and hook support. `winsdb_connect()` creates the database handle, obtains `wins_hook`, configures `LDB_FLG_NOSYNC` when requested, ensures the module list exists, reopens the database if needed, and sets the `winsdb_handle` opaque.

## Risks and Edge Cases

Address records are capped at 25, with registration replacing the oldest replica first and replication updates ignored at capacity. `winsdb_addr_decode()` mutates the LDB value buffer by inserting NULs at separators. Expiration is applied during decode for locally owned addresses rather than by a separate cleanup pass. `winsdb_set_maxVersion()` has nested transaction implications when called from add/modify. Corrupt DB records produce `NT_STATUS_INTERNAL_DB_CORRUPTION` and debug output. Static records override expiration, and unique records with multiple addresses are rewritten as multihomed during message encoding.

## Test Signals

Strong tests include DN round trips with scope/name/type, old address-string compatibility, dynamic address encode/decode, static records, address cap and sorting rules, expiration of locally owned versus replica SGROUP addresses, unique-to-MHOMED conversion, maxVersion allocation and monotonic updates, module-list insertion and reopen, hook invocation after commit, and transaction rollback on add/modify/delete failures.
