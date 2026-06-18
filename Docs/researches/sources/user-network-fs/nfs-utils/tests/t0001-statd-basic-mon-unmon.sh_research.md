# sources/user-network-fs/nfs-utils/tests/t0001-statd-basic-mon-unmon.sh

Purpose: This shell test exercises basic rpc.statd monitor and unmonitor behavior using the synthetic `nsm_client`.

Important APIs and control flow: It sources `test-lib.sh`, checks root and `/dev/log`, sets up temporary state, starts statd, issues monitor/unmonitor requests, dumps the stat database with `statdb_dump`, and validates expected record creation/deletion through shell assertions.

State, dependencies, and integration: It manipulates a temporary statd state directory, starts system daemons/binaries from the build tree, and depends on rpcbind/logging environment.

Risks and test signals: It likely requires root privileges and a working syslog socket, so CI may skip or fail outside privileged environments. Tests should verify cleanup traps, non-default state path isolation, statd lifecycle, and expected DB contents after each operation.
