<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0310_cancel_pdu.sh -->
# sources/user-network-fs/libsmb2/tests/test_0310_cancel_pdu.sh

Purpose: Integration test for cancelling an in-flight SMB2 PDU.

Important APIs, types, and functions: Runs `./prog_cat_cancel "${TESTURL}/CAT"`.

Control flow: Starts the cancellation-capable cat helper and expects it to complete without failure.

State and persistence behavior: No persistent local or remote state.

Dependencies and integration points: Depends on `prog_cat_cancel` and remote `CAT` fixture.

Risks: Timing-sensitive because the PDU must still be in flight for meaningful cancellation coverage.

Test signals: Direct cancellation path signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0310_cancel_pdu.sh -->
