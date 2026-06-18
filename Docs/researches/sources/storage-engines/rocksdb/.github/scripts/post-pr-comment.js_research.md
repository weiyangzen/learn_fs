<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/post-pr-comment.js -->
# Research: sources/storage-engines/rocksdb/.github/scripts/post-pr-comment.js

Purpose: Shared GitHub API utility for creating, updating, pruning, deleting, or superseding PR comments by marker.

Important APIs/types/functions: exports async `postPrComment` with `github`, `context`, `core`, `prNumber`, `body`, `marker`, optional `legacyMarkers`, `prunePrefix`, `preserveLatest`, `obsoleteMarker`, and `obsoleteTitle`. Internal helpers list comments, sort by activity time/id, identify obsolete comments, build obsolete bodies, delete comments, and supersede comments.

Control flow: validates input, ensures the marker is embedded, lists comments, updates an exact marker match if present, creates a fresh comment if update is absent or races with 404, then prunes related legacy/prefix comments while preserving the newest active comments.

State and persistence behavior: mutates GitHub issue comments through REST API calls. It does not write local files.

Dependencies and integration points: used by clang-tidy and AI review comment workflows through `actions/github-script`. Works with marker schemes from `ai-review-comment.yml`.

Risks: concurrent workflows can race between list/update/create/prune; the code handles 404 but still relies on ordering heuristics. Superseding preserves original bodies inside details, which can create very large comments. Marker collisions across bots would cause unintended updates.

Test signals: unit tests in `post-pr-comment.test.js` cover create/update, legacy migration, 404 races, and concurrent newer-comment supersession.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/post-pr-comment.js -->
