<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/cache-getdeps-downloads/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/cache-getdeps-downloads/action.yml

Purpose: Composite action that caches getdeps download archives to reduce mirror flakiness and speed Folly dependency builds.

Important APIs/types/functions: output `cache-hit`; single `actions/cache@v4` step stores `/tmp/rocksdb-getdeps-cache` with restore prefixes keyed by OS and architecture.

Control flow: the cache action restores any matching rolling cache before later getdeps operations populate or reuse the directory.

State and persistence behavior: caches downloaded source archives under `/tmp`, not compiled artifacts. The key includes `github.run_id`, so exact-key hits are unlikely and restore keys carry most reuse.

Dependencies and integration points: used by Folly-enabled PR and nightly jobs before `setup-folly`/`build-folly`; relies on `folly.mk` and getdeps honoring the same download cache path.

Risks: run-id keys create continuous new caches and depend on GitHub cache eviction policy. A poisoned or partial restored cache could affect dependency builds if getdeps does not validate downloads.

Test signals: cache logs and fewer dependency download failures during Folly setup are the practical signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/cache-getdeps-downloads/action.yml -->
