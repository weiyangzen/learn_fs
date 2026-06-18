
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/kms-site.xml

Purpose: placeholder Hadoop KMS configuration in the HDFS test image.

Important APIs/types/functions: empty `<configuration>` element.

Control flow: passive config file; no KMS properties are set.

State/persistence: none.

Dependencies/integration: copied to `/etc/hadoop/kms-site.xml` so Hadoop config paths are complete.

Risks: tests do not exercise a customized Hadoop KMS through this file.

Test signals: only config-load success.
