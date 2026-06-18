
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/krb5.conf

Purpose: client Kerberos configuration for the HDFS test image.

Important APIs/types/functions: sets default realm `KERBEROS.RCLONE`, disables DNS realm/KDC lookup, enables forwardable/proxiable tickets, and maps the realm to KDC `localhost`.

Control flow: read by Kerberos tools and Hadoop when `KERBEROS=true`.

State/persistence: no state; tickets are generated separately by `kinit` in `run.sh`.

Dependencies/integration: installed into `/etc/krb5.conf`; works with `kdc.conf` and generated principals.

Risks: localhost KDC assumption is specific to single-container tests.

Test signals: `kinit user` and `klist` in `run.sh` validate this client config.
