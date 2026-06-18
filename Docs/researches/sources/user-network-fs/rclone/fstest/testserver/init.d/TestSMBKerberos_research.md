
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSMBKerberos

Purpose: builds and starts a Samba AD DC container for SMB Kerberos integration tests using a host Kerberos config and credential cache.

Important APIs/types/functions: defines realm/domain, SMB/Kerberos ports, default `KRB5_CONFIG` and `KRB5CCNAME`, builds an Alpine image with `samba-dc`, provisions a domain, creates user `rclone`, configures shares, gets a Kerberos ticket cache, and emits SMB config with `use_kerberos=true`.

Control flow: inline Docker build, container run, host krb5.conf creation/copy, ccache generation/copy, KDC port rewrite, config echo.

State/persistence: writes `/tmp/rclone_krb5/krb5.conf` and ccache, builds a local Docker image, and runs a disposable container.

Dependencies/integration: Docker build/run, Samba tooling, Kerberos environment passed from `config.yaml`.

Risks: inline image build is expensive and can fail if Alpine packages change. Host `/tmp` Kerberos files can collide or become stale. Port conflicts on 28633/28634.

Test signals: SMB TCP probe plus successful Kerberos-authenticated SMB access.
