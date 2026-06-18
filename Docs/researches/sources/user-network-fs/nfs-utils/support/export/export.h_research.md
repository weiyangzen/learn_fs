# sources/user-network-fs/nfs-utils/support/export/export.h

## Purpose
Declares the mountd/exportd support surface for authentication, cache upcall processing, NFSv4 client monitoring, export cache updates, and client match helpers.

## Important APIs, Types, and Functions
Exports `auth_reload()`, `auth_authenticate()`, cache loop functions, `v4clients_*()` functions, `cache_get_filehandle()`, `cache_export()`, worker controls, client match helpers, and inline `is_ipaddr_client()`.

## Control Flow
The header defines contracts only. Runtime flow is implemented in auth/cache/v4clients modules: callers set fd bits, process ready descriptors, export cache answers, and match caller domains or `$`-prefixed IP-address pseudo-clients.

## State and Persistence Behavior
No state is stored here. Declared modules own their descriptors, workers, and caches.

## Dependencies and Integration Points
Includes `nfslib.h` and `exportfs.h`. It is shared by mountd/exportd support code and hides implementation modules behind one internal header.

## Risks and Edge Cases
Because this is an internal aggregate header, prototype drift can create build or ABI mismatches across support/export modules. `is_ipaddr_client()` assumes non-NULL, non-empty strings.

## Test Signals
Build all export support objects together and compile auth/cache/v4clients users. Add unit checks for `$` client-domain classification if callers begin accepting untrusted empty strings.
