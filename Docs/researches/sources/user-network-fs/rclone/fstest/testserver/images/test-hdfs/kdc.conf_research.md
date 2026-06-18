
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/kdc.conf

Purpose: minimal Kerberos KDC realm configuration for HDFS Kerberos integration tests.

Important APIs/types/functions: defines realm `KERBEROS.RCLONE` and points `acl_file` to `/etc/krb5kdc/kadm5.acl`.

Control flow: read by Kerberos KDC services when `run.sh` enables Kerberos setup.

State/persistence: KDC database is created at container runtime with `kdb5_util`; this file only defines realm metadata.

Dependencies/integration: Dockerfile installs it under `/etc/krb5kdc/`; `run.sh` creates principals and keytabs for HDFS and HTTP services.

Risks: test realm has hard-coded local settings and is not production-secure.

Test signals: successful KDC restart and principal creation in `run.sh` indicate the file is usable.
