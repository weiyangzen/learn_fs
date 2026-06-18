# sources/user-network-fs/samba/source3/nmbd/nmbd_lmhosts.c

## Purpose
Loads static NetBIOS name mappings from an `lmhosts` file into nmbd namelists and provides lookup support for those static entries. The mappings supplement dynamic broadcast/WINS discovery, especially for remote names.

## Important APIs, Types, And Functions
Public APIs are `load_lmhosts_file()` and `find_name_in_lmhosts()`. It uses `startlmhosts()`, `getlmhostsent()`, `endlmhosts()`, `struct sockaddr_storage`, `enum name_source LMHOSTS_NAME`, and `add_name_to_subnet()`.

## Control Flow
`load_lmhosts_file()` opens the file and iterates parsed entries under a talloc context. Non-IPv4 entries are skipped. For each IPv4 address, it chooses the first broadcast subnet whose mask matches the address, otherwise `remote_broadcast_subnet`. Entries without explicit type are inserted as permanent active `<00>` and `<20>` names; typed entries are inserted exactly. `find_name_in_lmhosts()` checks only `remote_broadcast_subnet` and returns active `LMHOSTS_NAME` records.

## State And Persistence
Loaded entries are inserted with `PERMANENT_TTL` and source `LMHOSTS_NAME`, so they do not expire normally. The lmhosts file remains authoritative persistence; in-memory records are rebuilt by loading.

## Dependencies, Risks, And Test Signals
`nmbd_namequery.c` checks lmhosts before subnet lookup. Risks include IPv4-only handling and unexpected subnet placement with overlapping masks. Test signals include default/explicit type loading, remote-broadcast lookup precedence, skipped non-IPv4 entries, and permanent TTL in `namelist.debug`.
