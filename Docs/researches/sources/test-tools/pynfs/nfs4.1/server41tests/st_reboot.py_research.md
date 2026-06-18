# sources/test-tools/pynfs/nfs4.1/server41tests/st_reboot.py

Purpose: non-standard reboot/grace-period tests for clientid/session invalidation, `CLAIM_PREVIOUS` reclaim, `RECLAIM_COMPLETE`, duplicate reclaim, multiple-client recovery, double reboot, and late reclaim near grace expiry.

Important APIs/types/functions: `_getleasetime`, `_waitForReboot`, local `create_session`, `reclaim_complete`, `testRebootValid`, `State`, `doTestOneClientGrace`, `doTestOneClientNoGrace`, `doTestAllClientsNoGrace`, `doTestRebootWithNClients`, and the `testRebootWith*` variants.

Control flow: tests create clients/sessions, complete normal reclaim, create confirmed open state, invoke `env.serverhelper(b"reboot")`, reconnect transport, clear cached sessions/clients, verify old sessions/clientids are stale, recreate clients, reclaim opens with `CLAIM_PREVIOUS`, send `RECLAIM_COMPLETE`, and probe whether new opens are blocked during grace and allowed after all clients recover. Multi-client variants scale to 10, 100, or 1000 clients and optionally reboot twice or reclaim twice.

State and persistence behavior: heavily stateful. It depends on server reboot persistence of reclaimable open state, lease time/grace state, clientid invalidation, session invalidation, and post-grace cleanup. It deliberately sleeps for lease time plus a buffer in `finally` blocks to leave the server in a clean state.

Dependencies/integration: requires a configured `serverhelper` capable of rebooting or restarting the target. Uses `rpc.rpc.RPCTimeout`, generated session/channel types, file/open helpers, and environment sleep/connect hooks.

Risks and test signals: expensive and disruptive; comments say reboot tests are not part of the standard suite. Large-client variants can stress server and test infrastructure. Timing around early grace lifting is logged as a warning rather than failed unless protocol status expectations are violated.
