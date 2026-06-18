<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_shared_cache02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_shared_cache02.py

Purpose: validates shared-cache reconfiguration semantics, especially pool size/reserve changes and rejection of absolute eviction values during reconfigure.

Important APIs/types/functions: `test_shared_cache02` has the same manual multi-connection harness as `test_shared_cache01`: `openConnections`, `closeConnections`, `add_records`, `wiredtiger_open`, `Connection.reconfigure`, and `assertRaisesWithMessage`.

Control flow: create two connections in a shared pool, write data, then reconfigure pool size successfully. Other tests start with a 50M pool and 20M reserves, attempt an over-quota reserve update that must fail, perform a valid reserve update, switch previously non-shared connections into a shared cache, and verify absolute `eviction_trigger`/`eviction_target` values are rejected while percentage values pass.

State and persistence behavior: state is primarily connection configuration and shared-cache pool accounting; table data is present to make the connections active and consume cache. Failed reconfigure must not corrupt the current pool configuration.

Dependencies/integration points: covers reconfiguration admission control, reserve accounting across multiple connections, and eviction percentage validation. Risks include test sensitivity to memory quotas and config parser messages; signals are successful reconfigure calls or exact expected `WiredTigerError` messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_shared_cache02.py -->
