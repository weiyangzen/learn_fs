<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/teardown-ccache/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/teardown-ccache/action.yml

Purpose: Post-build ccache cleanup and statistics reporting.

Important APIs/types/functions: checks `CCACHE_DIR`, runs `.github/scripts/ccache-trim.sh || true`, then `ccache -s || ...`; step is guarded with `if: always()`.

Control flow: if setup did not set `CCACHE_DIR`, it exits successfully; otherwise trims stale entries and prints stats.

State and persistence behavior: deletes unused ccache result/manifest files older than `.build_marker` and removes the marker. The remaining `.ccache` is what GitHub cache saves.

Dependencies and integration points: paired with `setup-ccache`; used by most ccache-enabled jobs.

Risks: trim failures are ignored, which preserves CI success but may allow cache growth. It assumes the script path exists and that ccache's file naming conventions match `ccache-trim.sh`.

Test signals: teardown logs show file count before/after trim and ccache stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/teardown-ccache/action.yml -->
