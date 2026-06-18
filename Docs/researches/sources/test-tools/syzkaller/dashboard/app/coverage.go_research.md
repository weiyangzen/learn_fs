# sources/test-tools/syzkaller/dashboard/app/coverage.go

Purpose: serves coverage heatmaps, per-file coverage views, coverage graphs, and coverage-subsystem regeneration for the dashboard.

Important APIs and types: `initCoverageDB` initializes the global Spanner coverage client in App Engine and leaves tests to inject a mock. `getCoverageDBClient`, `setWebGit`, and `getWebGit` are context-based injection points. `coverageHeatmapParams`, `makeHeatmapParams`, `getParam`, and `extractVal` parse coverage query parameters. `handleCoverageHeatmap` and `handleSubsystemsCoverageHeatmap` render regular and subsystem heatmaps; `handleHeatmap` performs shared validation, period generation, manager/subsystem loading, and template serving. `handleFileCoverage` validates file coverage query inputs, reads hit counts from coverage DB, optionally converts to unique coverage relative to all managers, fetches source through web-git, and renders annotated HTML. `handleCoverageGraph` renders monthly/quarterly coverage ratios. `handleUpdateCoverDBSubsystems` regenerates coverage DB subsystem labels from configured subsystem services.

Control flow: coverage pages start with `commonHeader`, require namespace coverage config, parse/validate period and filtering parameters, query Spanner through `coveragedb`, use cached manager lists and subsystem service lists for UI dimensions, and return either HTML templates or JSONL external coverage. File coverage has a stricter validation path using `pkg/validator` before DB and web-git access.

State and persistence behavior: primarily read-only against Spanner coverage DB and source repositories. `handleUpdateCoverDBSubsystems` mutates coverage DB records. The global coverage client is process state; tests inject a client through context. File-provider mocks are also context state.

Dependencies and integration points: depends on `pkg/cover`, `coveragedb`, `spannerclient`, `covermerger`, `urlutil`, validators, namespace coverage config, cached manager lists, subsystem services, templates, and App Engine context/logging.

Risks: generic parameter parsing ignores conversion errors in `extractVal`, so invalid ints/bools/dates can silently become zero values before later validation catches only some cases. Heatmap period count bounds are enforced, but file coverage requires exact date parse. Unique coverage performs an extra DB read in a specific order relied upon by tests. A nil global coverage client panics outside tests if initialization is missed.

Test signals: `coverage_test.go` validates bad request handling for malformed file coverage input, empty/regular DB rendering, unique-only multi-manager behavior, mock DB ordering, and mock web-git integration.
