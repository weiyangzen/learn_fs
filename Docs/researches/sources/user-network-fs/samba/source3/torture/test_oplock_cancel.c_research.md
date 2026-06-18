# sources/user-network-fs/samba/source3/torture/test_oplock_cancel.c

Purpose: This file tests cancellation of an SMB2/3 create request that is blocked by an oplock break. It verifies that canceling the create does not leave server state that prevents later cleanup and unlink.

Important APIs/types/functions: `create_cancel_send()` issues `cli_ntcreate_send()` and immediately calls `tevent_req_cancel()` on the subrequest. `create_cancel_done()` expects `cli_ntcreate_recv()` to return `NT_STATUS_CANCELLED`. `create_cancel()` wraps the async helper in a tevent poll. Public entrypoint is `run_oplock_cancel()`.

Control flow: The test opens two SMB connections with SMB1 disabled and oplocks enabled. `cli1` opens `oplock-cancel` for read, holding an oplock. `cli2` starts and cancels an open of the same file. After successful cancellation, `cli1` closes its handle and is freed, the test sleeps five seconds to let smbd instances communicate, and `cli2` unlinks the file.

State/persistence behavior: State includes a remote file, oplock state on the first connection, a canceled create request on the second connection, and delayed inter-smbd notification. The file is deleted at the end through `cli_unlink()`.

Dependencies and integration points: It depends on SMB2/3 client behavior (`CLI_FULL_CONNECTION_DISABLE_SMB1`), oplock support, async create cancellation, tevent NTSTATUS helpers, and Samba-specific smbd coordination. It tests a server behavior called out in comments as Samba-specific relative to Windows.

Risks: The comment says the test currently works only with SMB2/3 and Samba. The fixed five-second wait is timing-sensitive. If server cancel semantics change to ignore create cancel like Windows, the expected result may need revision.

Test signals: Passing requires the canceled create to complete as `NT_STATUS_CANCELLED`, no errors closing the original handle, and final unlink success after smbd coordination delay.
