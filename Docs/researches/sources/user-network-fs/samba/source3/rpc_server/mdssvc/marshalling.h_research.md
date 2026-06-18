# sources/user-network-fs/samba/source3/rpc_server/mdssvc/marshalling.h

## Purpose
This header defines the public Spotlight marshalling interface and the dalloc-backed type aliases used to represent Spotlight RPC values in memory.

## Important APIs, Types, And Functions
It defines blob size limits `MAX_SL_FRAGMENT_SIZE` and `MAX_MDSCMD_SIZE`, encoding flags `SL_ENC_LITTLE_ENDIAN`, `SL_ENC_BIG_ENDIAN`, and `SL_ENC_UTF_16`, aliases `sl_array_t`, `sl_dict_t`, `sl_filemeta_t`, `sl_nil_t`, `sl_bool_t`, `sl_time_t`, `sl_uuid_t`, and `sl_cnids_t`, plus the public functions `sl_pack_alloc()` and `sl_unpack()`.

## Control Flow
Callers build a dalloc tree using these type aliases, then call `sl_pack_alloc()` to create an `mdssvc_blob`. For inbound blobs, callers allocate an output `DALLOC_CTX` and call `sl_unpack()` to populate it with typed values.

## State And Persistence
The header declares in-memory types only. `sl_time_t` is `struct timeval`, `sl_uuid_t` is a 16-byte wrapper, and `sl_cnids_t` carries two metadata fields plus a dalloc array of CNIDs. Persistence is limited to the serialized blob produced by `sl_pack_alloc()`.

## Dependencies And Integration Points
It includes `dalloc.h`, NT status definitions, Samba `DATA_BLOB`, and generated mdssvc NDR structures. It is included by `dalloc.c`, `marshalling.c`, and mdssvc RPC code that exchanges Spotlight blobs.

## Risks And Test Signals
Risks include callers exceeding fragment limits, misuse of dalloc aliases as if they were distinct C structs, and assumptions about endian/UTF-16 flags that only `marshalling.c` enforces. Test signals include compile coverage for all aliases, boundary tests for `MAX_SL_FRAGMENT_SIZE` and `MAX_MDSCMD_SIZE`, and public API round trips from mdssvc RPC request/response blobs.
