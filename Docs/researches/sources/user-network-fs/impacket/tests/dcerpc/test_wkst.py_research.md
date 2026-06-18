# sources/user-network-fs/impacket/tests/dcerpc/test_wkst.py

## Purpose
This file tests Impacket's Workstation Service RPC (`wkst`) client definitions against a live `\\PIPE\\wkssvc` endpoint. It covers workstation info query/set, logged-on user and transport enumeration, use connection add/enum/get/delete, workstation statistics, domain join/unjoin/rename/name validation, alternate computer names, primary computer name, and computer-name enumeration.

## Important APIs, Types, and Functions
`WKSTTests` binds `wkst.MSRPC_UUID_WKST` over SMB named pipe and authenticates. It uses raw request classes such as `NetrWkstaGetInfo`, `NetrWkstaSetInfo`, `NetrUseAdd`, `NetrJoinDomain2`, and `NetrEnumerateComputerNames`, plus helper wrappers such as `hNetrWkstaGetInfo`, `hNetrUseAdd`, `hNetrValidateName2`, and `hNetrEnumerateComputerNames`. It constructs `LPUSE_INFO_1` for mapped-use tests and uses `NULL` for optional RPC pointers.

## Control Flow
Tests connect, populate request structures, submit them, and dump responses. Info-level tests repeat calls at levels 100, 101, 102, and 502. Set-info tests query level 502, save `wki502_dormant_file_limit`, set it to 500, verify by re-query, and restore. Use tests attempt to map local `Z:` to `\\\\127.0.0.1\\c$`, then enumerate, get info, and delete; they skip later calls for the NDR64 transfer syntax. Domain-management tests intentionally pass dummy credentials/password buffers and accept expected errors.

## State and Persistence Behavior
The suite can alter real workstation state. The level-502 dormant file limit is temporarily changed and restored. Use tests may add a local drive mapping. Domain join/unjoin/rename and alternate-name APIs are invoked but usually expect invalid-password/not-supported errors. No local persistent state is stored by the tests themselves.

## Dependencies and Integration Points
Dependencies include `impacket.dcerpc.v5.wkst`, shared remote test configuration, Windows Workstation Service, administrative `c$` share access on loopback, transfer syntax constants from `DCERPCTests`, and OS/domain policy behavior. Remote subclasses cover SMB NDR and NDR64.

## Risks
Some tests mutate workstation configuration or try domain-management calls; running against non-disposable hosts is risky. Use mapping cleanup is best-effort and may be skipped on access-denied or pipe-disconnected paths. Error validation relies heavily on string fragments such as `ERROR_INVALID_PASSWORD`, `0x8001011c`, and `ERROR_NOT_SUPPORTED`, which may vary. The NDR64 early return means use enum/get/delete coverage is intentionally incomplete for that syntax.

## Test Signals
Signals include successful info-level decoding, set/query/restore of workstation level 502, tolerated invalid-function/access-denied responses, expected domain-management failures with dummy credentials, and helper/raw parity across most operations. Remote marks and NDR/NDR64 subclasses identify it as an infrastructure-dependent integration suite.
