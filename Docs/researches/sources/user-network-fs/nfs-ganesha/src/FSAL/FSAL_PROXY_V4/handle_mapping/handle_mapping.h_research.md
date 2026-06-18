# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping.h

## Purpose
Declares the public handle-mapping API and NFSv3-facing digest format used by FSAL_PROXY_V4 when persistent handle mapping is compiled in.

## Important APIs, Types, and Functions
Defines `handle_map_param_t`, `nfs23_map_handle_t`, `PROXYV4_HANDLE_MAPPED`, `PROXYV4_HANDLE_MAXLEN`, error constants, and `HandleMap_Init/GetFH/SetFH/DelFH/Flush`.

## Control Flow
Consumers initialize once, store mappings when proxy handles are allocated, expand NFSv3 digests during wire-to-host conversion, delete stale mappings, and flush before shutdown.

## State and Persistence Behavior
The header only defines contracts. The digest is embedded in NFSv3 wire handles; backing persistence is implemented by sibling `.c` files.

## Dependencies and Integration Points
Includes `fsal.h` for buffer descriptors and FSAL context. Included by proxy method declarations and mapping implementation files.

## Risks
Digest layout uses native integer fields, so endian/layout expectations must be handled by the wider FSAL handle path. `synchronous_insert` is exposed but not truly implemented by the DB layer. The tests reference removed fields, showing API drift.

## Test Signals
Compile under `PROXYV4_HANDLE_MAPPING`, successful NFSv3 digest round trips, and stale returns for unknown digests.
