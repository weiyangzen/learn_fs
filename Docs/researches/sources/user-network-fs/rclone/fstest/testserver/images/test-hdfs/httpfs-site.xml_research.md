
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/httpfs-site.xml

Purpose: placeholder Hadoop HttpFS configuration for the HDFS test image.

Important APIs/types/functions: contains an empty `<configuration>` element.

Control flow: loaded passively if HttpFS components look for it; no properties alter behavior.

State/persistence: no state.

Dependencies/integration: copied into `/etc/hadoop/httpfs-site.xml` by the Dockerfile to satisfy expected Hadoop config file presence.

Risks: empty config means any HttpFS-specific behavior is default-only; this image primarily tests native HDFS access.

Test signals: absence of errors from Hadoop config loading is the only signal.
