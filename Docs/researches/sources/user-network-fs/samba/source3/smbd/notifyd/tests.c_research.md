# sources/user-network-fs/samba/source3/smbd/notifyd/tests.c

## Purpose
This is a standalone stress/smoke test program for notifyd message handling. It rapidly sends many add/delete registration changes and then pings notifyd to ensure the daemon remains responsive.

## Important APIs, Types, and Functions
The only function is `main()`. It uses `lp_load_global()`, `tevent_context_init()`, `messaging_init()`, `server_id_db_lookup_one()`, `messaging_send_iov()`, `messaging_read_send()`, `messaging_send_buf()`, and `tevent_req_poll()`.

## Control Flow
The program expects an smb.conf path argument, initializes logging/config/messaging, resolves `"notify-daemon"`, then loops 50,000 times. Each iteration sends a `MSG_SMB_NOTIFY_REC_CHANGE` add for `/tmpN` with all filters followed by a delete for the same path using zero filters. After the loop it waits for `MSG_PONG`, sends `MSG_PING` to notifyd, and polls until the pong arrives.

## State and Persistence
State is process-local. The test creates transient notifyd records and immediately deletes them. Its success condition is that notifyd processes the stream well enough to answer a later ping.

## Dependencies and Integration Points
It depends on notifyd message structs, Samba messaging, server-id names, and loadparm. `wscript_build` builds it as a non-installed `notifyd-tests` binary with `smbconf` dependency.

## Risks and Edge Cases
The path buffer is fixed at 64 bytes, which is sufficient for `/tmp49999`. The program does not inspect notifyd's database after the stress loop, so leaked entries would need separate detection. It exits on first send or polling failure and does not use the torture framework's richer assertions.

## Test Signals
This test is useful for catching crashes, backlog handling issues, and obvious add/delete throughput regressions. It does not validate event delivery, filters, or system watch registration.
