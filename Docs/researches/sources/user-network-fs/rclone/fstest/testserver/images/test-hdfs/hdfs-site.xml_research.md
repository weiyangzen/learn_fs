
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/hdfs-site.xml

Purpose: HDFS service configuration for the test image's single-container namenode/datanode setup.

Important APIs/types/functions: configures hostname usage, name/data directories, bind hosts, access-time precision, replication factor, safemode timing, and Kerberos principals/keytabs/data-transfer encryption within marker comments.

Control flow: declarative XML. The Kerberos block is removed by `run.sh` when not running Kerberos tests.

State/persistence: points namenode data to `/hadoop/dfs/name` and datanode data to `/hadoop/dfs/data`, which are container-local unless volumes are added.

Dependencies/integration: used by Hadoop daemons launched in `run.sh`; ports are exposed by `TestHdfs`.

Risks: replication is set to `2` in a one-container test environment, which may rely on pseudo/distributed behavior and could affect health timing. Encryption settings use test-compatible values.

Test signals: successful HDFS startup and readable/writable remote through rclone validate this configuration.
