<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/setup-ccache/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/setup-ccache/action.yml

Purpose: Configures ccache and GitHub cache restore for RocksDB C/C++ CI builds.

Important APIs/types/functions: inputs `cache-key-prefix` and `portable`; exports `CCACHE_DIR`, `CCACHE_BASEDIR`, `CCACHE_NOHASHDIR`, `CCACHE_COMPILERCHECK`, `CCACHE_SLOPPINESS`, `CCACHE_MAXSIZE`, and optionally `PORTABLE=1`; restores `${{ github.workspace }}/.ccache`; installs ccache; adds libexec/wrapper dir to PATH; zeros stats and touches `.build_marker`.

Control flow: environment is prepared, cache is restored by branch/SHA prefixes, ccache is installed if missing, PATH is adjusted per OS, and a marker is created for later trimming.

State and persistence behavior: `.ccache` is restored and later saved by `actions/cache`; `.build_marker` marks files used during the current build for `ccache-trim.sh`.

Dependencies and integration points: paired with `teardown-ccache`; used throughout PR jobs. Integrates with compiler wrapper lookup and RocksDB `PORTABLE` build mode.

Risks: cache keys include branch/ref and SHA, so restore behavior depends on prefix ordering. Large sloppiness settings trade correctness for hit rate and must match compiler behavior. `PORTABLE=1` is skipped for Folly linked jobs when caller sets `portable: false`.

Test signals: ccache stats in teardown, cache restore logs, and build commands resolving compiler wrappers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/setup-ccache/action.yml -->
