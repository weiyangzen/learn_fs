# sources/sync-backup/git-lfs/lfs/lfs.go

Purpose: package-level LFS environment reporting, tracing initialization, and reference-object linking.

Important APIs/types/functions: `Environ`, `init`, constants `gitExt`/`gitPtrPrefix`, and `LinkOrCopyFromReference`.

Control flow: `Environ` builds diagnostic/config environment lines from local paths, API transfer settings, endpoint access modes, manifest adapter names, fetch/prune config, include/exclude paths, extensions, and existing `GIT_` environment variables with overrides. `init` configures tracer defaults and maps transfer/curl trace env vars to `GIT_TRACE` when absent. `LinkOrCopyFromReference` checks whether an object already exists, then searches reference object paths and links/copies the first matching object into local media storage.

State/persistence behavior: `init` may set `GIT_TRACE` in process environment. `LinkOrCopyFromReference` can write/link local object files. `Environ` reads config and OS environment only.

Dependencies/integration: uses `config`, `lfsapi`, transfer queue manifests, filesystem helpers, and `tools.FileExistsOfSize`.

Risks/test signals: environment output can expose local paths and transfer settings. Reference linking must preserve object size correctness. Tests in `lfs_test.go` validate object enumeration through filesystem storage rather than this function directly.
