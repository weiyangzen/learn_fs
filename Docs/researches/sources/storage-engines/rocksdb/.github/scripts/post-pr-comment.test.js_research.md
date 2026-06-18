<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/post-pr-comment.test.js -->
# Research: sources/storage-engines/rocksdb/.github/scripts/post-pr-comment.test.js

Purpose: Node test suite for `post-pr-comment.js` comment creation, update, legacy migration, 404 handling, and supersession logic.

Important APIs/types/functions: uses `node:test`, `node:assert/strict`, `postPrComment`, constants `OBSOLETE_MARKER` and `OBSOLETE_TITLE`, harness helpers `makeComment`, `createHarness`, `createCore`, `escapeRegExp`, and `assertObsoleteComment`.

Control flow: each test builds an in-memory fake Octokit/context/core, calls `postPrComment` with different marker/pruning options, then asserts recorded update/create/delete calls and final fake comments. One test injects a new newer comment during the second pagination to simulate concurrent workflow behavior.

State and persistence behavior: all state is in-memory fake comments and call logs. No real GitHub API or filesystem is used.

Dependencies and integration points: validates the script used by `clang-tidy-comment.yml` and `ai-review-comment.yml`; runnable with modern Node's built-in test runner.

Risks: harness abstracts away pagination parameters, REST response details, rate limits, and permission failures. It does not test every branch, such as missing body/prNumber or delete-without-obsolete-title.

Test signals: `node --test .github/scripts/post-pr-comment.test.js` should pass and confirm stable comment marker behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/scripts/post-pr-comment.test.js -->
