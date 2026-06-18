# sources/sync-backup/git-lfs/t/cmd/git-credential-lfstest.go

Purpose: test credential helper implementing Git credential `get`, `store`, and `erase` behavior for HTTP auth scenarios.

Important APIs/types/functions: `credential`, `Serialize`, `fill`, `discoverCapabilities`, `credsForHostAndPath`, `parseOneCredential`, `credsFromFilename`, `log`, and `firstEntryForKey`.

Control flow: `main` dispatches by command. `get` parses key/value stdin into multi-value maps, resolves a credentials file by host or host/path under `CREDSDIR`, supports Windows drive path rewriting, filters credentials by advertised capabilities and username/state, optionally validates `wwwauth[]`, and emits credential key/value pairs plus capabilities. `store` and `erase` only log.

State/persistence behavior: reads static credential files; does not write credential stores. Uses `CREDSDIR` and `LFS_TEST_CREDS_WWWAUTH` environment variables.

Dependencies/integration: used by integration tests for Basic, bearer/authtype, stateful multistage auth, path-specific credentials, and www-authenticate propagation.

Risks: file format is compact and colon-delimited, so credentials containing colons are not supported. Scanner line length defaults apply.

Test signals: stderr logs `CREDS RECV/SEND`; exit status and stdout credentials drive client auth behavior.
