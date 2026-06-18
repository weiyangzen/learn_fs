# sources/sync-backup/git-lfs/lfshttp/certs_test.go

Purpose: Tests root CA discovery and SSL verification disabling from Git config and environment.

Important APIs/types/functions: Uses `getRootCAsForHostFromGitconfig`, `clientForHost`, `Client.HttpClient`, and `http.Transport.TLSClientConfig`.

Control flow: Tests write a temporary PEM certificate, configure CA info/path in Git or environment, and assert a non-nil cert pool for matching hosts. SSL verify tests construct clients and inspect `InsecureSkipVerify` on host transports.

State and persistence behavior: Uses temp files/directories for certificate fixtures. Client transport cache stores per-host HTTP clients during tests.

Dependencies and integration points: Validates `config.URLConfig` host matching, OS env settings (`GIT_SSL_CAINFO`, `GIT_SSL_CAPATH`, `GIT_SSL_NO_VERIFY`), and schannel settings.

Risks and edge cases: Host-specific CA config matches `git-lfs.local` but not host:port or unrelated hosts. Schannel defaults ignore CA info unless `schannelusesslcainfo` is enabled.

Test signals: Good coverage of root CA and verification toggles. Client-certificate loading and encrypted key decryption are not covered here.
