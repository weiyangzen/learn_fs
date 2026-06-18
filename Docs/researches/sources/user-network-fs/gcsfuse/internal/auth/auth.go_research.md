<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/auth.go -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/auth.go

Purpose: legacy OAuth2 token-source construction for GCS access, supporting service account key files, external token endpoints, ADC, and non-default universe domains.

Important APIs/types/functions: `UniverseDomainDefault`, `getUniverseDomain`, `newTokenSourceFromPath`, and `GetTokenSource`.

Control flow: `GetTokenSource` chooses key-file, token-url, or Google default token source. Key-file flow reads JSON, builds a JWT config, obtains universe domain through `google.CredentialsFromJSON`, and switches to self-signed JWT access tokens when the domain is not `googleapis.com`.

State and persistence: no persistent state; it reads credential files and returns token-source objects that may cache/reuse tokens depending on the underlying oauth2 implementation.

Dependencies: `golang.org/x/oauth2/google`, storage v1 full-control scope, local files, context, and the package's proxy token-source helper.

Risks: key files are sensitive; errors include file paths and parsing context. Non-default universe domain handling depends on Google library semantics. When both key-file and token-url are supplied, key-file wins.

Test signals: `auth_test.go` covers universe-domain extraction for Google, TPC, and invalid JSON; token-url behavior is covered in `token_source_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/auth.go -->
