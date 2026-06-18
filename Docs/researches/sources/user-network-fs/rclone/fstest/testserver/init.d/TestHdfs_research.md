
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestHdfs

Purpose: starts the local HDFS Docker test server and emits rclone HDFS config.

Important APIs/types/functions: `KERBEROS` env flag selects Kerberos mode. `start` runs image `rclone/test-hdfs` with hostname `rclone-hdfs`, maps HDFS/Kerberos ports to loopback, sleeps 30 seconds, optionally copies a Kerberos ticket cache, then prints `type=hdfs`, namenode, username, and `_connect`.

Control flow: lifecycle through `docker.bash`/`run.bash`; explicit sleep allows namenode/datanode startup before returning config.

State/persistence: disposable container; Kerberos mode copies `/tmp/krb5cc_<uid>` to host `/tmp`.

Dependencies/integration: depends on the HDFS image built from `images/test-hdfs`, Docker, and rclone HDFS backend tests.

Risks: fixed sleep can be too short/long. Port collisions on 8020/9866/88/750. Kerberos ticket cache path can collide with user state.

Test signals: TCP connect to `127.0.0.1:8020` and backend operations.
