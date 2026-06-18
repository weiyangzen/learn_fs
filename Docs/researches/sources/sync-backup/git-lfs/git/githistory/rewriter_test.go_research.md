# sources/sync-backup/git-lfs/git/githistory/rewriter_test.go

Purpose: comprehensive tests for history rewriting semantics.

Important APIs/types/functions: `NewRewriter`, `Rewrite`, `RewriteOptions`, `BlobFn`, `TreePreCallbackFn`, `TreeCallbackFn`, `WithFilter`, assertion helpers, and `CallbackCall`.

Control flow: tests rewrite fixture histories with blob transforms, tree additions, filters, callback collectors, and ref updates, then assert exact tree IDs, parent IDs, blob contents, visit counts, error propagation, and filter pointer identity.

State/persistence behavior: writes new objects and refs into temp fixture copies. Some tests rely on packed-object fixtures and annotated ancestry.

Dependencies/integration: uses fixture repositories and `gitobj`; tests exact SHA outputs, so they validate deterministic object writing and commit header preservation.

Risks/test signals: excellent coverage for core rewriting, but expensive and fixture-coupled. Exact SHA assertions are strong regression signals but require updates if fixture histories or object serialization changes intentionally.
