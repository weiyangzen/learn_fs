<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/scan.c -->
# sources/user-network-fs/samba/source4/torture/smb2/scan.c

## Purpose
`scan.c` is an SMB2 probing suite rather than a normal pass/fail behavioral test. It scans SMB2 opcode, getinfo, setinfo, and find information spaces to discover which values a target server accepts, rejects, or handles unusually. Its suite description explicitly says "scan target (not a test)".

## Important APIs, Types, And Functions
The suite contains `torture_smb2_getinfo_scan()`, `torture_smb2_setinfo_scan()`, `torture_smb2_find_scan()`, `torture_smb2_scan()`, and `torture_smb2_scan_init()`. It uses `struct smb2_tree`, `struct smb2_getinfo`, `struct smb2_setinfo`, `struct smb2_find`, `struct smb2_request`, `struct smb2_handle`, `smb2_getinfo()`, `smb2_setinfo()`, `smb2_find()`, `smb2_request_init_tree()`, `smb2_transport_send()`, `smb2_request_receive()`, and `smb2_request_destroy()`.

Setup helpers include `torture_smb2_connection()`, `smb2_connect()`, `torture_setup_complex_file()`, `torture_setup_complex_dir()`, `torture_smb2_testfile()`, `torture_smb2_testdir()`, `smb2_util_roothandle()`, and simple unlink/rmdir cleanup helpers. The scanner reads host/share settings, command-line credentials, resolver configuration, socket options, GENSEC settings, and SMB client options.

## Control Flow
`torture_smb2_getinfo_scan()` connects to the target, creates a complex file, stream, directory, and directory stream, opens file and directory handles, then loops `info_type` from 1 to 4 and `info_class` from 0 to 255. For both file and directory handles it calls `smb2_getinfo()` and logs any response that is not `NT_STATUS_INVALID_INFO_CLASS`, including returned blob length and a data dump.

`torture_smb2_setinfo_scan()` creates a complex file and alternate stream, opens the file, allocates a 1024-byte zero blob, and probes level values formed as `(info_class << 8) | info_type` for info types 1 through 4 and classes 0 through 255. It logs levels that are not rejected as `NT_STATUS_INVALID_INFO_CLASS`.

`torture_smb2_find_scan()` opens the share root, sets pattern `*`, restart continuation, and a 64 KiB response buffer, then scans find levels 1 through 255. It suppresses ordinary invalid, invalid-parameter, and not-supported statuses, logging and dumping any other responses.

`torture_smb2_scan()` connects manually, sets request timeout to three seconds, and sends raw SMB2 request bodies for opcodes 0 through 999. If the connection drops or times out, it reconnects and continues; otherwise it destroys the request and logs the returned status.

## State And Persistence
The getinfo and setinfo scanners create temporary `scan-getinfo.*` and `scan-setinfo.*` files and streams; find scans use the root handle only; opcode scanning maintains only connection/session state. Cleanup removes the main file and directory names, but alternate stream cleanup is mostly incidental to removing the base object.

## Dependencies And Integration Points
This file integrates with the SMB2 torture harness, low-level SMB2 transport constructors, Samba command-line credentials, resolver and loadparm contexts, and debug dumping. It is useful for protocol exploration, server fingerprinting, and regression investigation when a server starts accepting or rejecting a level differently.

## Risks
The opcode scan is intentionally aggressive and can disconnect the server, trigger unusual error paths, or produce noisy logs. It sends minimally initialized request bodies, so results are not always meaningful as standards conformance. The getinfo/setinfo/find scans can expose server bugs in information-level parsing and may produce large binary dumps. Because it treats many nonstandard responses as interesting rather than fatal, it is best run manually or in controlled diagnostics, not as a stable CI pass/fail suite.

## Test Signals
Primary signals are the logged "active opcode" statuses and the non-default info/find levels with blob lengths and dumps. Unexpected crashes, reconnect loops, hangs beyond the configured request timeout, or sudden changes in accepted info classes are the useful regression indicators.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/scan.c -->
