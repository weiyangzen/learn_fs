<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_cat_cancel.c -->
# sources/user-network-fs/libsmb2/tests/prog_cat_cancel.c

Purpose: Variant of the async cat test that cancels an in-flight read PDU to exercise cancellation handling.

Important APIs, types, and functions: Shares the cat callback structure and adds an open/read cancellation callback path that invokes libsmb2 PDU cancellation before normal close/disconnect.

Control flow: Connects and opens the file, starts a read, cancels the selected PDU path, then services the event loop until callbacks close/disconnect or mark completion.

State and persistence behavior: Uses global completion flag, buffer, offset, and transient SMB handle/PDU state. No persistence.

Dependencies and integration points: Integrated with `test_0310_cancel_pdu.sh` and sync/async cancellation behavior in libsmb2.

Risks: Cancellation races are sensitive to server speed and event-loop timing. As with `prog_cat`, weak exit status propagation can hide some error paths.

Test signals: Directly exercised by the cancel PDU shell test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_cat_cancel.c -->
