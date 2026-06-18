# sources/user-network-fs/samba/source3/nmbd/nmbd_namelistdb.c

## Purpose
Provides the core in-memory NetBIOS name database used by nmbd subnets. It normalizes names, adds/removes/fetches records, updates TTLs and IP lists, implements standard registration/release callbacks, expires stale names, adds Samba magic names, and dumps diagnostics.

## Important APIs, Types, And Functions
Defines global `samba_nb_type` and public functions `set_samba_nb_type()`, `remove_name_from_namelist()`, `find_name_on_subnet()`, `find_name_for_remote_broadcast_subnet()`, `update_name_ttl()`, `add_name_to_subnet()`, `standard_success_register()`, `standard_fail_register()`, `find_ip_in_name_record()`, `add_ip_to_name_record()`, `remove_ip_from_name_record()`, `standard_success_release()`, `expire_names()`, `add_samba_names_to_subnet()`, `dump_name_record()`, and `dump_all_namelists()`.

## Control Flow
`set_samba_nb_type()` selects hybrid node type when WINS is involved, otherwise broadcast node type. `add_name_to_subnet()` allocates and uppercases a record, sets flags/source/IPs/TTL metadata, and inserts into a normal subnet or WINS storage. Lookup uppercases requests and optionally filters to self/permanent names. Standard callbacks create/update self names after registration, remove failed registrations, and remove released IPs. Expiry extends expired self names instead of deleting them and removes other stale records. Magic names include `*<00>`, `*<20>`, `__SAMBA__<20>`, and `__SAMBA__<00>`.

## State And Persistence
Normal subnet state is linked-list memory plus `subrec->namelist_changed`; WINS subnet state is persisted by WINS-specific helpers. `dump_all_namelists()` writes `namelist.debug` under the lock path.

## Dependencies, Risks, And Test Signals
All name, query, registration, release, lmhosts, and browser-role modules depend on this file. Risks include conversion failures, IP-list allocation failures, inconsistent change flags, self-name expiry hiding refresh bugs, and duplicate magic names. Test signals include add/find/remove by type/scope, self-only filtering, TTL calculations, IP add/remove behavior, non-self expiry, and debug dump content.
