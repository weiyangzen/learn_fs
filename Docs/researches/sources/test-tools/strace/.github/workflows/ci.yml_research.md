<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/.github/workflows/ci.yml -->
# sources/test-tools/strace/.github/workflows/ci.yml

Purpose: primary GitHub Actions CI for strace, covering whitespace validation, coverage, and a large compiler/architecture/stacktrace build matrix.

Important jobs: `whitespace-errors` checks `git diff-index --check --cached` against the empty tree. `coverage` installs dependencies, runs `ci/run-build-and-tests.sh`, and uploads gcov results to Codecov using OIDC. `build-check` uses a matrix of GCC 9-15, Clang 14-19, musl-gcc, x86/x86_64/aarch64 targets, kheaders/libdw/libunwind/nostacktrace variants, and Ubuntu x86/arm runners.

Control flow: triggers on push and pull request. Workflow-level concurrency cancels older runs per PR/ref. Matrix entries set `CC`, `TARGET`, and a variant-derived `STACKTRACE`/`KHEADERS` environment before invoking common CI scripts.

State and persistence: persists CI artifacts only through Codecov upload; normal build outputs are runner-local.

Dependencies and integration: depends on pinned GitHub actions, Ubuntu packages installed by `ci/install-dependencies.sh`, kernel headers when `KHEADERS` is set, and strace's build/test scripts.

Risks: matrix breadth is expensive and runner availability may dominate feedback time. Pinned action SHAs need Dependabot upkeep. The whitespace job uses `--cached` against checkout state, which is unusual for pushed commits but effective for tree whitespace validation. Test signals: green matrix jobs across compiler versions, successful coverage upload, and variant-specific failures tied to `CC/TARGET/STACKTRACE`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/.github/workflows/ci.yml -->
