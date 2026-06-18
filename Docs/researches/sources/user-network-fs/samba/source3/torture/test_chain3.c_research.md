# sources/user-network-fs/samba/source3/torture/test_chain3.c

Purpose: This file tests SMB1 chained AndX request handling while an oplock break is in flight. `run_chain3()` starts an asynchronous workflow that opens `chain3.txt` with a batch oplock, waits for the oplock break, then submits a chained open/write/close sequence against the same file to exercise request ordering and cleanup in smbd's chain handling.

Important APIs/types/functions: `struct chain3_andx_state` tracks the chained open fnum, write count, and string payload. `chain3_andx_send()` builds three linked SMB1 requests with `cli_openx_create()`, `cli_write_andx_create()`, and `cli_smb1_close_create()`, then dispatches them with `smb1cli_req_chain_submit()`. `chain3_send()` sets up the outer test, uses `cli_smb_oplock_break_waiter_send()`, `cli_ntcreate_send()`, and then calls the AndX helper. The public entrypoint is `run_chain3()`.

Control flow: `run_chain3()` creates a tevent context and polls the outer request. The first phase opens a torture SMB connection and registers an oplock-break waiter. The second phase creates the file with `REQUEST_OPLOCK|REQUEST_BATCH_OPLOCK`. Once the create succeeds, the code submits the chained open/write/close sequence; in parallel the oplock break callback closes the broken fnum. Completion is reported through `chain3_recv()`.

State/persistence behavior: Runtime state is held in talloc-owned tevent request objects and a single remote test file. The chained request stores `"hello"` including its terminator and persists it briefly to the share. The test depends on server-side oplock state, file handles, and SMB1 request chain state; it frees local subrequests as callbacks complete but does not explicitly unlink the test file in this file.

Dependencies and integration points: The test integrates with Samba's torture connection helpers, `async_smb.h`, tevent NTSTATUS helpers, SMB1 client chain helpers, oplock break waiting, and SMB security constants. It is registered as a torture test by the surrounding harness through `run_chain3()`.

Risks: Timing sensitivity is high because oplock break delivery and chained request completion race by design. The test assumes SMB1 support and a Samba server with oplock behavior; dialect restrictions or disabled oplocks make it unrepresentative. Failures can indicate request-chain ordering bugs, stale fnum handling, or oplock cleanup regressions.

Test signals: Passing requires `cli_ntcreate`, oplock break receive/close, chained open/write/close, and final tevent polling to all return successful NTSTATUS values. Diagnostic prints include each callback's returned status and fnum/write counts, making protocol sequencing failures visible.
