
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/core-site.xml

Purpose: Hadoop core-site configuration for the HDFS test image.

Important APIs/types/functions: sets `fs.defaultFS` to `hdfs://localhost:8020`, configures static HTTP user/proxy settings for root, and includes a Kerberos block enabling authentication, authorization, RPC integrity, and static user group mapping.

Control flow: declarative XML consumed by Hadoop at startup. `run.sh` removes the Kerberos-marked block when `KERBEROS=false`.

State/persistence: no direct state; controls Hadoop process behavior in the container.

Dependencies/integration: copied by the Dockerfile into `/etc/hadoop/core-site.xml`; paired with `hdfs-site.xml` and `krb5.conf`.

Risks: permissive proxy host setting and static mapping are test-only. Kerberos markers must remain intact for `sed` removal to work.

Test signals: correct config lets rclone HDFS tests connect to the local namenode with or without Kerberos.
