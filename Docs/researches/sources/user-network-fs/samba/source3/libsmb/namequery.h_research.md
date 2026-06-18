# sources/user-network-fs/samba/source3/libsmb/namequery.h

## Purpose
This header declares the public name-query and name-resolution surface implemented by `namequery.c` for source3 SMB client code. It centralizes APIs for server affinity, NetBIOS node status, NetBIOS name queries, WINS/broadcast resolution, generic resolver dispatch, and DC/KDC list discovery.

## Important APIs, Types, And Functions
The declarations expose SAF functions, tevent send/recv pairs for `node_status_query`, `name_query`, `name_resolve_bcast`, and `resolve_wins`, synchronous wrappers for those operations, address list utilities such as `remove_duplicate_addrs2`, general helpers `internal_resolve_name`, `resolve_name`, `resolve_name_list`, and domain helpers `find_master_ip`, `get_pdc_ip`, `get_sorted_dc_list`, and `get_kdc_list`.

The API uses Samba core types: `TALLOC_CTX`, `struct tevent_context`, `struct tevent_req`, `NTSTATUS`, `struct nmb_name`, `struct node_status`, `struct node_status_extra`, `struct sockaddr_storage`, and `struct samba_sockaddr`.

## Control Flow And Integration
Callers can choose async send/recv pairs when integrating into an existing tevent loop or synchronous wrappers when blocking is acceptable. Lower-level APIs return raw `sockaddr_storage` lists and flags; higher-level APIs return `struct samba_sockaddr` arrays suitable for connection code. The header is included by `namecache.c`, `namequery_dc.c`, and other libsmb/client modules needing NetBIOS or DC resolution.

## State And Persistence
The header has no runtime state. It exposes functions that read and write gencache-backed SAF/namecache state and use loadparm configuration internally.

## Dependencies
It includes `includes.h` and `<tevent.h>` and assumes the broader Samba include graph provides definitions for `NTSTATUS`, talloc, NetBIOS name/status structures, and socket structures.

## Risks And Test Signals
The main API risk is ownership and representation mismatch: returned arrays are talloc-owned by the supplied context, counts use both `size_t` and `unsigned int`, and some APIs return `sockaddr_storage` while others return `samba_sockaddr`. Compile coverage should include C files that consume every declaration, and behavioral tests should exercise both async and synchronous wrappers.
