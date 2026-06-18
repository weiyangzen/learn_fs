# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestBlockTokensCLI.java

Purpose: secure HA integration tests for Ozone admin CLI operations around block-token secret keys: OM fetch-key and SCM rotate-key with and without force.

Important APIs/types/functions: `init`, `testFetchKeyOMAdminCommand`, `testFetchKeyOMAdminCommandUtil`, `testRotateKeySCMAdminCommandWithForceFlag`, `testRotateKeySCMAdminCommandWithoutForceFlag`, `testRotateKeySCMAdminCommandUtil`, `shouldRotate`, `createArgsForCommand`, secure setup helpers, and `startCluster`. It uses `OzoneAdmin`, `MiniKdc`, `MiniOzoneHAClusterImpl`, `SecretKeyManager`, `ManagedSecretKey`, `ScmConfig`, `SCMHTTPServerConfig`, and config diffing via Guava `Maps.difference`.

Control flow: setup gets the admin command's configuration, starts MiniKdc, sets secure Kerberos principals/keytabs, enables block/container tokens, starts a 3-SCM/3-OM HA secure cluster with service IDs, and creates a client. Fetch-key redirects `System.out` to a byte stream, runs `ozoneAdmin.execute("om", "fetch-key", "--service-id=...")`, parses `Current Secret Key ID:`, and compares it to the active SCM secret key. Rotate tests wait for SCM leader, construct host:port and augmented `--set=key=value` args for secure/HA config differences, run `scm rotate`, and compare current secret key before/after based on `--force` or elapsed rotation duration.

State and persistence: process global stdout is temporarily replaced, MiniKdc keytabs and secure cluster state are created, SCM secret key manager current key may rotate, and admin command configuration is patched through CLI `--set` options.

Dependencies and integration points: Ozone admin shell, SCM/OM HA service IDs, Kerberos configuration, SCM secret-key rotation policy, and `SecretKeyConfig.parseRotateDuration`.

Risks: `System.setOut(System.out)` after redirection does not preserve the original PrintStream if it was already changed; a local saved original would be safer. Non-force rotation can be timing-sensitive because it depends on current key age. Config diff only handles entries present on the secure test config and absent from default admin config.

Test signals: fetched UUID equals active SCM current key ID; forced rotate changes current key; non-forced rotate changes only if configured rotation duration has elapsed; cluster leader presence is awaited.
