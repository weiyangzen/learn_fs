# sources/object-store/minio/cmd/sftp-server_test.go

Purpose: This file tests SFTP authentication behavior for MinIO internal users/service accounts and LDAP users. It verifies password and public-key paths, policy requirements, suffix behavior, and failure cases.

Important APIs and types: `MockConnMeta` implements `ssh.ConnMetadata` with a configurable username. `newSSHConnMock` constructs metadata. `TestSFTPAuthentication` runs the IAM test suites. Suite methods call `sshPasswordAuth` and `sshPubKeyAuth`, use admin APIs to create users/policies, and read public keys from `testdata`.

Control flow: The top-level test starts each IAM suite, runs service-account success and invalid-password checks, then skips LDAP cases unless `EnvTestLDAPServer` is set. When LDAP is available it configures LDAP, verifies missing policy and invalid user failures, verifies forced service-account suffix failure for an LDAP user, verifies invalid password failure, attaches LDAP policies and verifies password login for two users, then tests LDAP public-key success, invalid key failure, and no-public-key failure.

State and persistence behavior: Tests create IAM users, attach policies, add canned policies, attach LDAP policies, and rely on LDAP-backed identities. LDAP successful auth creates temporary credentials through the production auth path. Temporary server state is torn down by suite teardown.

Dependencies and integration points: The tests integrate the MinIO admin client, IAM test harness, optional external LDAP test server, SSH public key parsing, SFTP auth callbacks, and LDAP policy mapping. They do not start a full SFTP listener or exercise the SFTP driver.

Risks: LDAP coverage is environment-gated and skipped unless a test LDAP server is configured. Tests depend on fixed LDAP fixture users such as `dillon` and `fahim` and fixed key files. The non-LDAP portion primarily tests service-account password logic.

Test signals: Expected signals are successful service-account auth with and without `=svc`, `errAuthentication` for wrong service-account passwords, LDAP missing-policy errors, `errNoSuchUser` for invalid/fallback users, successful LDAP password auth after policy attachment, successful LDAP public-key auth for a user with `sshPublicKey`, `errAuthentication` for mismatched keys, and failure for users lacking an SSH public-key attribute.
