# sources/user-network-fs/samba/source4/smb_server/tcon.c

## Purpose
This file manages common `smbsrv_tcon` allocation, lookup, initialization, and destruction for both SMB1 and SMB2. It owns TID id-tree setup and ensures NTVFS disconnect is called when a tree connection is freed.

## Important APIs, Types, And Functions
Public functions are `smbsrv_smb_init_tcons`, `smbsrv_smb2_init_tcons`, `smbsrv_smb_tcon_find`, `smbsrv_smb2_tcon_find`, `smbsrv_smb_tcon_new`, and `smbsrv_smb2_tcon_new`. Internal support includes `smbsrv_init_tcons`, `smbsrv_tcon_find`, `smbsrv_tcon_destructor`, and `smbsrv_tcon_new`.

## Control Flow
Initialization creates an idr context, masks the requested limit to 24 bits, stores the limit, and clears the list. Lookup rejects zero and out-of-range TIDs, fetches from idr, type-checks, and updates last-request time. Allocation chooses memory owner and handle id limit based on SMB1 connection vs SMB2 session, allocates the tcon, stores share name, initializes handle tracking, assigns a random TID in range, links it, sets a destructor, and records connect time. Destruction logs remote address/share, disconnects NTVFS if present, removes the TID from the correct context, and unlinks the tcon.

## State And Persistence
The file mutates in-memory tcon id trees and linked lists and owns tcon lifetime. It does not persist share state, but NTVFS disconnect may flush/close backend state.

## Dependencies And Integration Points
It depends on idtree random allocation, talloc destructors, dlink lists, NTVFS disconnect, stream connection remote addresses, and handle initialization from the common handle module. SMB2 `tcon.c` and SMB1 tree-connect code allocate and find tcons through these APIs.

## Risks And Test Signals
Risks include 24-bit id limit truncation, random TID allocation exhaustion, destructor behavior with already-cleared NTVFS contexts, SMB2 session-owned memory assumptions, and handle cleanup ordering. Tests should create many tcons, find invalid/zero/out-of-range TIDs, disconnect with active NTVFS, compare SMB1 vs SMB2 ownership, and verify TID reuse after free.
