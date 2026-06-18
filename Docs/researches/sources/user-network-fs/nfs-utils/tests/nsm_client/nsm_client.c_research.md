# sources/user-network-fs/nfs-utils/tests/nsm_client/nsm_client.c

Purpose: `nsm_client.c` is a synthetic command-line NSM client plus NLM notification server for exercising rpc.statd behavior.

Important APIs and control flow: `main` parses host/name/program/version options and dispatches `daemon`, `crash`, `stat`, `notify`, `unmon_all`, `unmon`, or `mon`. `nsm_client_get_rpcclient` resolves the statd host, asks rpcbind for `SM_PROG/SM_VERS`, and creates a UDP RPC client. Command helpers call generated NSM stubs. `daemon_simulator` registers NLM callback services, and `nlm_sm_notify_3_svc`/`nlm_sm_notify_4_svc` print received reboot notifications.

State, dependencies, and integration: It depends on generated `nlm_sm_inter` files, libtirpc/SunRPC, nfs-utils RPC helpers, and statd running locally or remotely.

Risks and test signals: The getopt switch lacks `break` statements, so one option falls through and can unintentionally set later fields. Some argument-count checks are too low for commands that read two extra args. Tests should cover each command, option parsing, invalid cookies, rpcbind failures, and daemon callback receipt.
