# sources/test-tools/syzkaller/dashboard/app/coverage_test.go

Purpose: tests per-file coverage rendering and validation paths from `coverage.go`.

Important tests and helpers: `setCoverageDBClient` injects a Spanner client mock into context. `TestFileCoverage_BadRequest` sends a malformed `dateto` parameter and asserts an HTTP 400. `TestFileCoverage` table-tests empty DB, normal DB, and unique-only multi-manager DB behavior, verifying rendered HTML contains expected annotated line/count strings. `staticFileProvider` mocks kernel source retrieval. `emptyCoverageDBFixture`, `coverageDBFixture`, `multiManagerCovDBFixture`, and `newRowIteratorMock` model Spanner row iterators and read-only transactions.

Control flow under test: namespace coverage mocks are installed, the handler receives GET requests to `/test2/coverage/file`, validates params, reads coverage rows from mocked Spanner, reads source from mocked web-git, and renders file coverage HTML.

State and persistence behavior: no real persistence is used; all DB and source state is supplied by mocks. The multi-manager fixture deliberately expects two ordered Spanner reads: selected manager first, all-manager coverage second for `unique-only`.

Dependencies and integration points: uses `coveragedb` mock types, `spannerclient` interfaces, `covermerger.FileVersProvider`, testify assertions/mocks, App Engine test context, and dashboard coverage config test helpers.

Risks covered: malformed request rejection, empty coverage rendering, hit-count alignment with source lines, and unique coverage subtraction semantics. Gaps include heatmap rendering, coverage graph rendering, JSONL output, subsystem regeneration, and real web-git/Gerrit base64 behavior.
