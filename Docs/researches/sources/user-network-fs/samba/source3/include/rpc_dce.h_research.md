# sources/user-network-fs/samba/source3/include/rpc_dce.h

## Purpose
`rpc_dce.h` defines DCE/RPC fragment and header constants used by source3 RPC code. It captures Samba's maximum signing trailer size, selected maximum PDU fragment length, fixed RPC header length, and endianness markers.

## Important APIs, Types, And Control Flow
There are no functions or structs. Important constants are `RPC_MAX_SIGN_SIZE` (56 bytes), `RPC_MAX_PDU_FRAG_LEN` (`0x10b8`, matching Windows 2000 behavior per the comment), `RPC_HEADER_LEN` (16), and byte-order flags `RPC_BIG_ENDIAN` and `RPC_LITTLE_ENDIAN`.

## State And Persistence
The header contains no state. Its constants govern transient RPC PDU allocation, fragmentation, signing space reservation, and marshalling decisions.

## Dependencies And Integration Points
It integrates with RPC server/client fragment generation, DCE/RPC bind and request handling, signing/sealing code, and generated NDR marshalling that needs fragment size limits.

## Risks And Test Signals
Risks include fragment sizes incompatible with clients, insufficient signing trailer reservation, assuming little-endian data where big-endian is negotiated, and memory sizing errors around fixed header length. Test signals include RPC bind/request fragmentation, signed and unsigned calls, large spoolss/LSA/SAMR requests near fragment boundaries, endian marker parsing, and interoperability with Windows clients expecting the selected fragment size.
