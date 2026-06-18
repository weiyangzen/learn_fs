# sources/storage-engines/pebble/Makefile

## Purpose
The Pebble Makefile centralizes common developer and CI commands for tests, coverage, stress, crossversion testing, s390x emulation, Bazel metadata generation, generated test data, docs serving, module updates, cleaning, and formatting.

## Important APIs, types, and functions
Top-level variables include `GO`, `PKG`, `GOFLAGS`, `STRESSFLAGS`, `TAGS`, `TESTS`, and `COVER_PROFILE`. Key targets include `test`, `testcoverage`, `testrace`, `testasan`, `testmsan`, `testnocgo`, `testobjiotracing`, `lint`, `stress`, `stressrace`, `stressmeta`, `crossversion-meta`, `stress-crossversion`, `test-s390x-qemu`, `gen-bazel`, `clean-bazel`, `generate`, `generate-test-data`, `testdocs`, `mod-update`, `clean`, `git-clean-check`, `mod-tidy-check`, `format`, and `format-check`.

## Control flow
Most targets layer extra `testflags`, tags, or variable overrides before delegating to `go test`. Stress targets use `-exec stress`. Crossversion metadata fetches release branches, checks out the latest release, compiles old and head metamorphic binaries, and runs `TestMetaCrossVersion`. s390x invokes Docker under QEMU. Formatting installs `crlfmt` and checks for a clean git diff.

## State and persistence behavior
Targets can create coverage profiles, test binaries, WORKSPACE/BUILD files, generated test fixtures, modified Go module files, formatting changes, and Docker/Go caches. CI check targets intentionally require a clean git tree before running and fail if changes appear.

## Dependencies and integration points
GitHub workflows call many of these targets. The file integrates Go tooling, CockroachDB stress, Bazel Gazelle, Docker/QEMU for s390x, Python docs serving, `go generate`, and internal repository scripts/tools.

## Risks and edge cases
There are two `generate` target declarations; make merges rules but this is easy to misread. `git_dirty` is evaluated at parse time, so cleanliness checks reflect state when Make starts. `crossversion-meta` performs git checkouts inside the working tree and can disrupt local state if interrupted. `clean` removes test binaries by package basename only.

## Test signals
CI relies on this Makefile for the canonical pass/fail signals. Local validation usually starts with `make test`, then adds `make testrace`, `make mod-tidy-check`, `make format-check`, and specialized targets for touched areas.
