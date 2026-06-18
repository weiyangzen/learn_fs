# sources/sync-backup/git-lfs/lfsapi/endpoint_finder_test.go

Purpose: Validates endpoint resolution, access-mode configuration, URL parsing, and alias replacement for LFS API endpoints.

Important APIs/types/functions: Tests `Endpoint`, `RemoteEndpoint`, `NewEndpoint`, `NewEndpointFromCloneURL`, `AccessFor`, `SetAccess`, `ExtractRemoteUrl`, and `ReplaceUrlAlias`.

Control flow: Tests construct `lfshttp.Context` objects with synthetic Git config and assert returned endpoint URL, SSH metadata, operation, and access modes. Table-driven cases cover bare SSH, bracketed ports, remote helpers, and `insteadOf`/`pushInsteadOf`.

State and persistence behavior: Access tests mutate in-memory Git config through `SetAccess`. Local-path tests create temp directories with or without `.git` to exercise file URL rewriting.

Dependencies and integration points: Integrates with `lfshttp.Endpoint`, `ssh.SSHMetadata`, `creds`, runtime OS detection, and `os.Stat`.

Risks and edge cases: Windows local path behavior is skipped due path canonicalization differences. Tests cover invalid FETCH_HEAD lines and remote URL extraction but not actual `parseFetchHead` filesystem fallback.

Test signals: Strong coverage of endpoint precedence and parsing. Helps prevent regressions in remote push URL and alias behavior.
