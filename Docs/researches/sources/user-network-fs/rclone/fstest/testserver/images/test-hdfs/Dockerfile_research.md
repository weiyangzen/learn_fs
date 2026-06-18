
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/Dockerfile

Purpose: builds a minimal Debian-based HDFS Docker image for rclone HDFS integration tests, with optional Kerberos support.

Important APIs/types/functions: installs OpenJDK 8, curl, Python, Kerberos KDC/admin packages; downloads Hadoop 3.2.1; configures `JAVA_HOME`, `HADOOP_HOME`, `HADOOP_CONF_DIR`, `PATH`, and Hadoop data/name directories; adds Hadoop XML configs, Kerberos configs, ACL, and `run.sh`.

Control flow: package install, Hadoop download/extract, symlink `/etc/hadoop`, create data/log directories, copy configs, make `run.sh` executable, and set it as `CMD`.

State/persistence: image contains Hadoop under `/opt`, configs under `/etc`, and runtime data directories under `/hadoop*`. Containers started from it format namenode state at runtime.

Dependencies/integration: used by `init.d/TestHdfs`, which runs image `rclone/test-hdfs` and maps HDFS/Kerberos ports.

Risks: Debian stretch and Hadoop 3.2.1 are old; download URL availability and image rebuild reliability are external dependencies. Embedded test Kerberos realm is intentionally insecure and local-only.

Test signals: successful container startup exposes namenode `127.0.0.1:8020` and optional KDC state for HDFS backend tests.
