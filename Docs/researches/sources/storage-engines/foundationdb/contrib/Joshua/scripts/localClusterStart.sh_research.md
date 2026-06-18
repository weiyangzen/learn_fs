# sources/storage-engines/foundationdb/contrib/Joshua/scripts/localClusterStart.sh

Purpose: starts a local single-process FoundationDB cluster for Joshua-related scripts. It prepares work/log/config directories, writes an `fdb.cluster` file, starts `fdbserver`, configures a `single memory` database, verifies availability, and can stop the process.

Important APIs/functions: environment variables configure paths and behavior: `WORKDIR`, `LOGDIR`, `ETCDIR`, `BINDIR`, `FDBPORTSTART`, `FDBPORTTOTAL`, `SERVERCHECKS`, `CONFIGUREWAIT`, `FDBCLUSTERTEXT`, `AUDITCLUSTER`, `AUDITLOG`. Functions are `log`, `displayMessage`, `createDirectories`, `createClusterFile`, `startFdbServer`, `getStatus`, `verifyAvailable`, `createDatabase`, `startCluster`, and `stopCluster`.

Control flow: if `FDBCLUSTERTEXT` is absent it randomizes a loopback IP and port. `startCluster` sequences directory creation, cluster file generation, server launch, and database configuration. Availability is checked through `fdbcli status json`.

State and persistence: writes under `${SCRIPTDIR}/tmp/fdb.work` by default, with cluster config, logs, and data directories. It keeps the server PID in `FDBSERVERID` shell state and optionally writes audit log lines.

Dependencies and integration: requires executable `fdbserver` and `fdbcli` in `BINDIR`, bash, coreutils, and port availability. Other Joshua scripts can source or call it to get a local cluster file.

Risks and test signals: random ports can collide; `createDatabase` logs but ignores final availability failure; chmod scans broad script patterns; process cleanup relies on a valid PID. Test signals are `fdbclient.log`, `startcluster.log`, `database_available=true`, and successful `fdbcli` operations.
