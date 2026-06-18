
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/mapred-site.xml

Purpose: minimal MapReduce/YARN configuration for the HDFS image.

Important APIs/types/functions: sets `mapreduce.framework.name` to `yarn` and binds the node manager to `0.0.0.0`.

Control flow: declarative Hadoop config.

State/persistence: none.

Dependencies/integration: copied into `/etc/hadoop` with other configs, although rclone HDFS tests mainly require HDFS daemons.

Risks: minimal YARN config may not be enough for real MapReduce workloads; it is test-image support only.

Test signals: absence of Hadoop config errors.
