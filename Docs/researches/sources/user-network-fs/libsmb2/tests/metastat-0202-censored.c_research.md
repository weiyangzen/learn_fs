<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/metastat-0202-censored.c -->
# sources/user-network-fs/libsmb2/tests/metastat-0202-censored.c

Purpose: Concurrency test program that queues multiple SMB2 stat requests on one connection, aimed at SMB 2.0.2 credit/overdraw behavior.

Important APIs, types, and functions: Defines `struct op`, `struct cbwrap`, `stat_cb`, `service_loop`, `usage`, and `main`. Uses `smb2_stat_async`, `smb2_service`, URL parsing, password option, and a pending counter.

Control flow: The program parses a base SMB URL plus filenames, connects to the share, queues all stat operations, polls until callbacks decrement `pending`, then reports failures.

State and persistence behavior: State is arrays of per-operation status/stat buffers and callback wrappers allocated per queued request. Network session state lives in libsmb2 context.

Dependencies and integration points: Integrated with `test_0400_overdrawn_0202.sh`, which runs several instances concurrently against discovered filenames.

Risks: Requires a live SMB server and valid URL. Pending counter mutation is single-threaded through the event loop, but callbacks allocate/free wrappers per request and can leak only if requests never complete before process exit.

Test signals: Direct test signal is successful completion under concurrent shell orchestration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/metastat-0202-censored.c -->
