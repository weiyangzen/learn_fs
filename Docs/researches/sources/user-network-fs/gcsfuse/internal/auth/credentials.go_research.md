<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/credentials.go -->
# Research: sources/user-network-fs/gcsfuse/internal/auth/credentials.go

Purpose: newer cloud auth credentials discovery path using `cloud.google.com/go/auth/credentials`.

Important APIs/types/functions: package `scope` is `storage.ScopeFullControl`; private `getCredentials` builds `credentials.DetectOptions`; exported `GetCredentials` calls `credentials.DetectDefault`.

Control flow: caller-provided key file is passed as `CredentialsFile`; empty key file allows Application Default Credentials and metadata-server discovery. Errors are wrapped as credential-detection failures.

State and persistence: no persistent state; the returned `*auth.Credentials` may internally cache tokens according to the auth library.

Dependencies: Cloud auth library, Cloud Storage full-control scope, and environment/metadata server behavior in `DetectDefault`.

Risks: full-control scope is broad. ADC discovery can contact metadata services in real deployments. Key-file precedence and empty-string behavior are part of the public contract.

Test signals: `credentials_test.go` injects a mock detector to verify options and error wrapping without external services.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/auth/credentials.go -->
