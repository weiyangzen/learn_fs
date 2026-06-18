<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nlmtest/nlmtest.c -->
# sources/user-network-fs/nfs-utils/tools/nlmtest/nlmtest.c

## Purpose

`nlmtest.c` is a legacy manual test client for the Network Lock Manager protocol. It creates an RPC client to lockd, constructs NLM test/lock/unlock requests, and reports lock status and conflicts.

## Important APIs, Types, and Functions

`main` parses `-b`, `-f`, `-h`, `-l`, `-o`, `-p`, `-u`, and `-x`, creates an `NLM_PROG`/`NLM_VERS` UDP client, prepares `nlm_testargs`, `nlm_lockargs`, or `nlm_unlockargs`, and calls generated RPC stubs `nlm_test_1`, `nlm_lock_1`, and `nlm_unlock_1`. `makelock`, `makeowner`, and `makefileh` build protocol structures. `nlm_stat_name` and `holderstr` format responses.

## Control Flow

The tool first sends `NLM_TEST` for the requested range. If the test is denied it prints holder details. Unless the test failed and the user did not request blocking or unlock behavior, it then sends either `NLM_UNLOCK` or `NLM_LOCK` and prints the result.

## State and Persistence Behavior

The program does not persist local state. It can create or remove remote lock state in lockd through NLM calls. Cookie, owner handle, PID, and file handle content are process-local request fields.

## Dependencies and Integration Points

It depends on generated `nlm_prot.h` stubs, ONC RPC client APIs, `<nfs/nfs.h>`, `host.h` defaults, and an NFS/lockd test server. It is distributed but not built in the normal tree.

## Risks and Edge Cases

`makefileh` contains `#error this needs updating if it is still wanted`, so the file intentionally does not compile as-is. File-handle construction is stale and partly hard-coded. The `-f` filename option is parsed but not used by `makefileh`. Integer formatting uses `%d` for offsets/lengths that may be wider than int. UDP and NLMv1-only behavior limit modern coverage.

## Test Signals

Before any runtime testing, compilation must be restored. Then tests should cover granted, denied, unlock, blocking flags, exclusive/shared locks, owner encoding, file-handle generation, and server unavailability paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nlmtest/nlmtest.c -->
