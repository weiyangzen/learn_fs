<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0400_overdrawn_0202.sh -->
# sources/user-network-fs/libsmb2/tests/test_0400_overdrawn_0202.sh

Purpose: Stress test for SMB 2.0.2 credit handling by issuing many parallel stat operations.

Important APIs, types, and functions: Uses `../utils/smb2-ls` to discover a filename and runs `metastat-0202-censored` concurrently in loops.

Control flow: Discovers a file in the share, starts multiple background metastat processes with repeated filename arguments, waits for all PIDs, and fails if any process exits nonzero.

State and persistence behavior: No intended persistent state. Uses shell arrays of background PIDs.

Dependencies and integration points: Depends on live SMB 2.0.2-capable server behavior, `smb2-ls`, and metastat helper.

Risks: Discovery parses the first token from `smb2-ls`, which can be brittle. High concurrency can be environment-sensitive.

Test signals: Concurrent stat success is the direct stress signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0400_overdrawn_0202.sh -->
