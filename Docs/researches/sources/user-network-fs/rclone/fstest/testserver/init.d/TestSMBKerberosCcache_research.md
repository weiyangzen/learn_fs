
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSMBKerberosCcache

Purpose: variant of SMB Kerberos test server that passes an explicit `kerberos_ccache` rclone config value instead of relying solely on `KRB5CCNAME`.

Important APIs/types/functions: defaults `KRB5_CONFIG` and `RCLONE_TEST_CUSTOM_CCACHE_LOCATION` under `/tmp/rclone_krb5_ccache`, builds a Samba AD DC image, creates a Kerberos ticket cache, and emits `kerberos_ccache=<path>`.

Control flow: same provisioning model as `TestSMBKerberos`, with separate ports `28637`/`28638` and separate temp directory.

State/persistence: writes krb5.conf and ccache to host `/tmp`, builds image `rclone/test-smb-kerberos-ccache`, and runs a disposable container.

Dependencies/integration: used by `test_all/config.yaml` with `KRB5_CONFIG` env; validates rclone SMB ccache option handling.

Risks: same Docker/Samba/Kerberos drift risks, plus stale explicit ccache file can affect repeated runs.

Test signals: config emission includes `kerberos_ccache`; integration tests confirm auth through that cache.
