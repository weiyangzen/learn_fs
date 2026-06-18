# sources/user-network-fs/samba/source3/nmbd/nmbd.h

## Purpose
`nmbd.h` is the central header for Samba's NetBIOS name service daemon. It defines constants, enums, state structures, callback types, subnet traversal macros, WINS record layout, and includes generated nmbd prototypes.

## Important APIs, Types, and Functions
The header defines database keys (`INFO_*`, `ENTRY_PREFIX`), timing constants, browser/election constants, mailslot paths, name source enum, master/domain/logon states, and subnet types. Core structures include `nmb_data`, `name_record`, `browse_cache_record`, `server_info_struct`, `server_record`, `work_record`, `userdata_struct`, `response_record`, `subnet_record`, and `WINS_RECORD`. It defines callback typedefs for response, timeout, success, and fail handlers, including specific register/release/refresh/query/node-status signatures. It declares external subnet globals and includes `nmbd/nmbd_proto.h`.

## Control Flow
This header shapes nmbd control flow by defining how names live on subnets, how workgroups and servers age and announce, how response records retry/expire, and how callbacks are typed for asynchronous name operations. Macros such as `FIRST_SUBNET`, `NEXT_SUBNET_EXCLUDING_UNICAST`, and `NEXT_SUBNET_INCLUDING_UNICAST` drive subnet iteration.

## State and Persistence
The structures describe in-memory daemon state. `WINS_RECORD` is the packed-ish record used between nmbd and WINS replication logic. TTL/death/refresh fields determine persistence in memory and eventual database writes performed elsewhere.

## Dependencies and Integration Points
It includes `libsmb/nmblib.h` and generated `nmbd_proto.h`. `SYNC_DNS` is defined here when `HAVE_PIPE` is unavailable, affecting `asyncdns.c`. Almost every nmbd source file depends on these common state definitions.

## Risks
Because this is a shared internal header, structure layout changes have broad daemon impact. `userdata_struct` uses a flexible array plus explicit 16-byte alignment workaround for older GCC, so allocation/copy/free functions must respect its layout. `WINS_RECORD` has fixed limits such as 25 IPs and 17-byte names. IPv4-specific helpers and fields reflect nmbd's IPv4 NetBIOS focus.

## Test Signals
Compile-time prototype checking is important for callback typedefs. Behavioral tests should exercise response record lifecycle, subnet iteration including/excluding unicast, WINS record serialization limits, userdata copy/free ownership, and state transitions for browser/domain/logon roles.
