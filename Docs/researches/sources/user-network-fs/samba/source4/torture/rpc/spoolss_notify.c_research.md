# sources/user-network-fs/samba/source4/torture/rpc/spoolss_notify.c

## Purpose

`spoolss_notify.c` tests spoolss printer change-notification callback behavior. It starts an in-process DCE/RPC callback server that implements a minimal spoolss endpoint, subscribes to remote printer change notifications, records callback packets, and verifies the server sends expected `ReplyOpenPrinter` and `ReplyClosePrinter` calls.

## Important APIs, Types, and Functions

The callback server is represented by `notify_test_spoolss_interface` and callback table `srv_cb`. Server hooks include `spoolss__op_ndr_pull()`, `spoolss__op_dispatch()`, `spoolss__op_ndr_push()`, `spoolss__op_init_server()`, and interface lookup functions by UUID/name. Stub implementations `_spoolss_ReplyOpenPrinter()`, `_spoolss_ReplyClosePrinter()`, and `_spoolss_RouterReplyPrinterEx()` return successful callback responses. `struct received_packet` and the global `received_packets` list retain observed callback opnums and decoded requests. Client-side helpers cover `OpenPrinter`, `RemoteFindFirstPrinterChangeNotifyEx`, and `RouterRefreshPrinterChangeNotify`.

## Control Flow

`test_RFFPCNEx()` clears any stale packet list, starts a local SMB/DCE/RPC server via `test_start_dcerpc_server()`, opens the remote print server, subscribes using `RemoteFindFirstPrinterChangeNotifyEx()` with a print-server notify option, asserts a `NDR_SPOOLSS_REPLYOPENPRINTER` callback arrived, refreshes notifications twice, closes the printer, and asserts the last callback is `NDR_SPOOLSS_REPLYCLOSEPRINTER`. `test_ReplyOpenPrinter()` directly calls the server implementation path and then closes the returned handle; it skips Samba 3 because it is testing Samba 4 server internals.

## State and Persistence Behavior

The test starts local listener state, registers a DCE/RPC endpoint server, and temporarily changes the loadparm setting `dcerpc endpoint servers` to `spoolss`. It does not intentionally persist remote printer state. Callback packets are allocated under the NULL talloc context so they survive request contexts, then are freed by `free_received_packets()`. If the process aborts before cleanup, only process-local listener and memory state are lost.

## Dependencies and Integration Points

The file integrates client spoolss stubs with the Samba DCE/RPC server runtime, SMB server socket setup, process model initialization, endpoint registration, interface discovery, NTVFS initialization, network interface selection, and generated spoolss NDR tables.

## Risks and Edge Cases

The test relies on a usable local IPv4 interface and on the remote spooler being able to connect back to the worker's callback address. Firewalls, NAT, interface ordering, or binding restrictions can cause false failures. `received_packets` is a global list and assumes single-threaded test execution. The callback dispatch hard-codes opnums 58, 60, and 66, so IDL changes or alternate protocol versions would break it. Several richer printer-level notification paths are compiled out.

## Test Signals

Passing `testRFFPCNEx` proves callback endpoint registration, remote subscription, callback NDR decoding, and close notification all work together. Passing `testReplyOpenPrinter` verifies the server-side reply calls return handles and close cleanly on Samba 4.
