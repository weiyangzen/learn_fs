# sources/user-network-fs/samba/source3/lib/privileges.c

## Purpose
This file implements source3 privilege assignment storage and lookup. It maps SIDs to Samba security privilege bitmasks in the account policy database and exposes helpers used by LSA privilege enumeration, grant, revoke, and account management paths.

## Important APIs, Types, And Functions
Records are keyed as `PRIV_<SID>` and store an eight-byte little-endian privilege mask. `map_old_SE_PRIV()` preserves compatibility with older 16-byte `SE_PRIV` records written in native byte order. `get_privileges()` and `set_privileges()` are the private database accessors gated by `lp_enable_privileges()` and `get_account_pol_db()`. Public APIs include `get_privileges_for_sids()`, `get_privileges_for_sid_as_set()`, `privilege_enumerate_accounts()`, `privilege_enum_sids()`, `grant_privilege_by_name()`, `grant_privilege_set()`, `revoke_privilege_set()`, `revoke_all_privileges()`, `revoke_privilege_by_name()`, `privilege_create_account()`, `privilege_delete_account()`, `is_privileged_sid()`, and `grant_all_privileges()`.

## Control Flow
Lookup fetches one SID record, decodes old or current formats, and returns false for disabled privileges, absent database, absent key, or malformed data. Enumeration traverses the account policy DB, filters keys by prefix, optionally filters by a requested privilege mask, rejects the invalid `S-0-0` SID, parses SIDs, and accumulates them in a talloc-owned array. Grants OR new masks into existing masks; revokes clear bits; deleting an account removes the key.

## State And Persistence
Privilege assignments are durable in Samba's account policy database through dbwrap. No transaction grouping is used around read-modify-write grant/revoke operations in this file, so concurrent updates can race unless callers serialize them elsewhere.

## Dependencies And Integration Points
It depends on dbwrap, passdb account-policy access, SID utilities, privilege conversion helpers from `libcli/security/privileges_private.h`, and loadparm `enable privileges`. It feeds LSA RPC semantics through `PRIVILEGE_SET` conversion.

## Risks And Test Signals
Important risks include disabled privilege mode silently returning no records, malformed legacy records, read-modify-write lost updates, accepting zero-mask accounts as privileged accounts, and byte-order compatibility. Tests should cover current and old record formats, grant/revoke by name and set, enumeration filtered by one privilege, malformed SID/key rejection, `lp_enable_privileges()` false behavior, and concurrent grant/revoke if a higher layer promises serialization.
