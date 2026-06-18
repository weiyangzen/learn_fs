<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/ccache-trim.sh -->
# Research: sources/storage-engines/rocksdb/.github/scripts/ccache-trim.sh

Purpose: CI script that trims ccache to entries accessed or created during the current build.

Important APIs/types/functions: requires `CCACHE_DIR`; uses `.build_marker`; counts files named `*R` or `*M`, deletes result/manifest files not newer than the marker, removes empty directories, runs `ccache -c`, prints before/after counts, and deletes the marker.

Control flow: exits early if marker is absent; otherwise performs cleanup under `set -e` with best-effort directory cleanup and counter recalculation.

State and persistence behavior: mutates the ccache directory by deleting stale result and manifest files. It intentionally does not touch local build outputs.

Dependencies and integration points: called by `teardown-ccache/action.yml` after `setup-ccache` creates the marker. Depends on ccache's on-disk file suffixes and `find`.

Risks: intended only for CI; local shared ccache use could lose useful entries. Future ccache storage layout changes could make the file pattern incomplete or dangerous. If the marker timestamp is wrong, it can over-trim or under-trim.

Test signals: teardown log line `ccache-trim: before -> after` and subsequent cache size/stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/ccache-trim.sh -->
