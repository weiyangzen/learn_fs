# Research: sources/storage-engines/wiredtiger/test/evergreen.yml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009062`: lines 1-7779, `Docs/researches/chunks/subset-b-009062_research.md`
- `subset-b-009063`: lines 7780-7839, `Docs/researches/chunks/subset-b-009063_research.md`

## Chunk Research

### subset-b-009062: lines 1-7779

# sources/storage-engines/wiredtiger/test/evergreen.yml lines 1-7779

## Scope

This chunk covers almost the entire WiredTiger Evergreen project configuration: global task hooks, reusable Evergreen functions, shared variable anchors, the full visible `tasks:` catalog, and `buildvariants:` from `ubuntu2004` through the start of `amazon2023-arm64-msan`. The source file has 7,839 lines; this chunk stops at line 7,779 while the `amazon2023-arm64-msan` buildvariant is still being declared, so later lines must be consulted for the end of that variant and any following variants.

## Purpose

The file is the CI contract for WiredTiger in Evergreen. It maps source checkout, build configuration, compilation, test execution, artifact movement, diagnostics, statistics publishing, and platform selection into Evergreen primitives. Rather than implementing application logic, it composes shell scripts and repository tools into a large scheduler matrix.

The top-level settings enable `stepback`, establish `pre` cleanup/environment setup, define `post` diagnostic and upload hooks, and install a timeout hook that invokes the WiredTiger hang analyzer. The default execution timeout is six hours, with specific tasks overriding it for stress, memory-model, coverage, and long performance jobs.

## Important Evergreen Surfaces

### Global Hooks

- `pre` always runs `cleanup` and `setup environment`, so task bodies can assume a fresh checkout location and common expansions such as `PREPARE_TEST_ENV` and `PREPARE_PATH`.
- `post` uploads stack traces, format configs, model workloads, stderr/stdout, stat files, generic task artifacts, and hang-analyzer outputs. This makes failed test homes and diagnostics persistent in S3.
- `timeout` runs `run wt hang analyzer`, which collects core/debugger output from `wiredtiger/cmake_build` when a task stops making progress.

### Functions

The `functions:` block is the primary API surface. Important reusable functions include:

- Environment and project setup: `setup environment`, `get project`, `generate github token`, `get automation-scripts`, `checkout develop`, `get engflow creds`.
- Build functions: `configure wiredtiger`, `python config check`, `make wiredtiger`, `compile wiredtiger`, `compile wiredtiger develop`, `compile mongodb`, `compile wiredtiger docs`.
- Artifact movement: `fetch artifacts`, `fetch endian format artifacts`, `upload artifact`, `upload artifact for compatibility test`, `upload wtperf test artifact`, `upload endian format artifacts`, `upload stacktraces`, `upload stat files`.
- Test wrappers: `make check directory`, `make check all`, `unit test`, `unit test tsan parallel`, `format test`, `format test script`, `format test disagg`, `checkpoint test`, `checkpoint stress test`, `cppsuite test`, `cppsuite perf test`, `csuite test`, `model test`, `run-perf-test`, `run workgen test`.
- Reporting and metrics: `code coverage analysis`, `run code coverage tests`, `code coverage publish report`, `code coverage publish main page`, `upload stats to atlas`, `upload stats to evergreen`, `validate-expected-stats`, `tsan warning metric`.
- Integration helpers: `fetch mongo repo`, `import wiredtiger into mongo`, `fetch mongo-tests repo`, `build and push antithesis container`, `verify wt datafiles`, `verify wt datafiles with binary`.

These functions use Evergreen expansion syntax heavily. Values such as `${build_variant}`, `${revision}`, `${build_id}`, `${execution}`, `${dependent_task|compile}`, `${CMAKE_BUILD_TYPE|}`, and `${num_jobs}` form the implicit parameter interface between variants, tasks, and shell scripts.

### Variable Anchors and Templates

The `variables:` section defines YAML anchors reused by tasks and variants:

- Built-in extension flags set CMake options for LZ4, Snappy, Zlib, and Zstd.
- Static-library anchors toggle `ENABLE_SHARED` and `ENABLE_STATIC`.
- Sanitizer anchors set ASan build type, clang preset, cppsuite disabling, and tcmalloc exclusion.
- The macOS template supplies Xcode clang, Homebrew LLVM environment, dyld library path, and a standard task list.
- Stress-test templates define repeated task shapes for format stress, ASan stress, race-condition stress, recovery stress, disaggregated format stress, and workgen tests.

The anchors make the task catalog compact but create a dependency between template changes and many task names produced later via YAML merge (`<<: *anchor`).

## Control Flow

The common task flow is:

1. Checkout `wiredtiger` with `git.get_project`.
2. Configure with CMake through `configure wiredtiger`.
3. Build with Ninja, Make, or the Windows PowerShell helper through `make wiredtiger`.
4. Either upload the complete build as `wiredtiger.tgz` or run tests directly.
5. Dependent test tasks fetch the compile artifact from S3 and run in the extracted `wiredtiger` tree.
6. Post hooks collect stack traces, configs, stat files, stdout/stderr, and task artifacts regardless of the specific task body.

Compilation control flow branches on OS and variant settings. Windows calls `test/evergreen/build_windows.ps1`; macOS injects Python library/include paths discovered through `find_libpython`; Linux prefers CMake presets when `CMakePresets.json` exists and otherwise falls back to explicit `CC` and `CXX`. TCMalloc is installed or downloaded only when `ENABLE_TCMALLOC=1`, and sanitizer builds explicitly disable it.

Test control flow is mostly task-selected. `make check all` invokes CTest labels, `unit test` builds include/exclude lists from fail-list files before calling `test/suite/run.py`, `unit test tsan parallel` uses `tools/pytest_parallel`, format tests execute either `test/format/t` or `format.sh`, cppsuite tasks run from `cmake_build/test/cppsuite`, and perf tasks run `bench/perf_run_py/perf_run.py` twice to produce both Evergreen and Atlas JSON outputs.

Buildvariants then select task subsets by name, tag expression, distro override, `batchtime`, `cron`, and variant-local expansions. For example, Ubuntu 20.04 runs broad PR, lint, long, compatibility, workgen, model, and live-restore coverage; sanitizer variants narrow the matrix and inject sanitizer options; non-standalone variants add `WT_STANDALONE_BUILD=0` and unit-test hooks; ARM64/Amazon variants repeat major coverage on different host pools.

## State and Persistence Behavior

Persistent state is almost entirely external to this YAML and mediated through Evergreen expansions and S3:

- Compile tasks upload build artifacts under `wiredtiger/${build_variant}/${revision}/artifacts/${task_name}_${build_id}${postfix|}.tgz`.
- Test tasks fetch compile or data artifacts by `dependent_task`, build variant, revision, build id, and optional postfix.
- Format configs, model workloads, stack traces, stat files, hang-analyzer outputs, coverage reports, perf JSON, WT_TEST homes, datafiles, and compatibility directories are uploaded for later inspection.
- Long performance tests intentionally persist populated WT homes and backups for downstream no-create or live-restore tasks.
- Documentation update tasks clone `wiredtiger.github.com`, rsync generated docs by branch, commit changes as the doc bot, and push through a generated GitHub App credential.
- Atlas/Evergreen metrics upload functions persist performance, code coverage, complexity, modularity, and TSAN-warning records with task metadata.

Transient local state includes `wiredtiger/`, `mongo/`, `mongo-tests/`, `automation-scripts/`, virtualenvs, `cmake_build`, `WT_TEST*`, temporary fail-list files, and coverage build directories. The `cleanup` function removes `wiredtiger` and `wiredtiger.tgz`, but many task-specific directories are intentionally archived before cleanup.

## Dependencies and Integration Points

Key external dependencies include Evergreen commands (`git.get_project`, `expansions.update`, `s3.get`, `s3.put`, `archive.targz_pack`, `subprocess.exec`, `github.generate_token`, `timeout.update`), AWS/S3 credentials, GitHub token generation, MongoDB toolchain v5, CMake, Ninja/Make, Python 3.11/3.13 depending on platform, virtualenv, pip packages, Bazel/EngFlow credentials for MongoDB integration, and platform-specific hosts such as Windows 2022, macOS 14 ARM64, RHEL 8, Ubuntu 20.04/22.04, zSeries, PPC, Amazon 2023 ARM64.

Repository integration is broad. The YAML delegates behavior to many checked-in scripts and tools, including `test/evergreen/*`, `test/suite/run.py`, `tools/pytest_parallel`, `bench/perf_run_py/*`, `bench/workgen/runner/*.py`, `test/format/*`, `test/cppsuite`, `test/csuite`, `test/compatibility/*`, `dist/s_all`, `dist/s_docs`, `dist/s_release`, `dist/modstat`, `tools/antithesis`, and MongoDB/mongo-tests repositories for integration and large-scale tests.

The file also integrates with Evergreen task tagging. Tags such as `pull_request`, `python`, `unit_test`, `unit_test_xsan`, `unit_test_tsan`, `unit_test_disagg`, `cppsuite-stress-test`, `cppsuite-perf-test`, `stress-test-*`, `stress-test-disagg`, `data-validation-stress-test`, `model_checking`, `workgen-test`, `pull_request_code_statistics`, and perf category tags are the main grouping mechanism for variant task selection.

## Task Families and Test Signals

The visible task catalog provides several distinct quality signals:

- Build and compiler coverage: default compile, develop compile, static/dynamic production toggles, GCC/Clang version sweeps, uncommon build flags, configure-combinations, minimal-extension builds, static WT utility validation.
- CMake/CTest coverage: make-check-all, per-directory tests for examples, checkpoint, cursor order, fops, format, huge, manydbs, packing, readonly, salvage, thread, wtperf, catch2, and csuite labels.
- Python suite coverage: normal buckets, long buckets, XSAN buckets, random-seed tests, hook tests for timestamp, tiered, timing stress, parallel checkpoint, disaggregated leader/follower/table-prefix/key-provider, TSAN-specific parallel runs, and macOS Python config validation.
- Stress coverage: format stress, format predictable replay, schema abort predictable replay, checkpoint stress, recovery stress, split/skiplist stress, data validation checkpoint matrix, disaggregated leader/follower/switch modes, abort recovery, race-condition ASan, PPC/zSeries-specific format stress.
- Compatibility and persistence coverage: release compatibility tests, upgrade/daily/weekly/patch/import modes, compatibility against develop, endian datafile generation/verification across little/big-endian variants, WT datafile verification with different binaries.
- Coverage/statistics: parallel code coverage buckets, merged coverage report, per-test coverage, Catch2 coverage, code-change PR report, cyclomatic complexity, modularity metrics, TSAN warning metrics.
- Performance: wtperf btree/oplog/checkpoint/stress/eviction/log/YCSB tests, long 500m btree workflows, live-restore perf, cppsuite perf, disaggregated failover perf, many-dhandle stress, prefetch verify microbenchmarks, workgen tests, and wt2853 perf tests.
- Integration: MongoDB many-collection test using imported WiredTiger, docs compile/update, package task, Antithesis container build/push.

## Risks and Maintenance Concerns

- The YAML is a single large scheduler specification. Small expansion or anchor changes can affect many tasks and variants through YAML merges and tag expressions.
- Many shell snippets rely on Evergreen expansion defaults. Empty expansions can change command-line shape; the `unit test` function already works around this by copying `${unit_test_ignore}` into a local variable before testing `-n`.
- Artifact names couple producers and consumers through `build_variant`, `revision`, `build_id`, `dependent_task`, and `postfix`. Renaming compile tasks, changing postfixes, or moving upload paths can break downstream fetches.
- Sanitizer behavior is fragile. Comments call out hidden ASan/TSan warnings under parallel execution, TSAN deadlock false positives, MSAN false positives from uninstrumented libraries, and sanitizer/tcmalloc incompatibility.
- Platform-specific branches are dense: Windows uses PowerShell and Cygwin paths, macOS constructs Python library paths manually, RHEL PPC strips ZSTD and disables mmap in some format runs, big-endian variants disable ZSTD, and Amazon/Ubuntu ARM64 variants override distros.
- Some buildvariant task references in this chunk name `generate-tsan-metric-timestamp` and `generate-tsan-metric-disagg-timestamp`, but those task definitions are not visible in lines 1-7779. They may appear after the chunk, be generated elsewhere, or be stale references; the merge lane should verify the complete file.
- The chunk ends mid-`amazon2023-arm64-msan` buildvariant, so any conclusions about that variant's task list are incomplete until the following chunk is merged.
- Several tasks intentionally ignore failures or alter expected failures for coverage or sanitizer collection. This is useful for metrics but can obscure task health if propagated to the wrong variant.
- Documentation update and Atlas upload tasks handle secrets; several functions avoid verbose mode or use `silent: true`, but changes to logging could expose credentials.

## Research Notes for Merge Lane

This chunk establishes the high-level structure and almost all names needed by a final per-file report. The merge lane should combine this with the trailing chunk to confirm the complete buildvariant list, especially the rest of `amazon2023-arm64-msan`, `amazon2023-arm64-ubsan`, and `amazon2023-stress-nonstandalone`, which are only partially or not fully covered by this line range.

### subset-b-009063: lines 7780-7839

# sources/storage-engines/wiredtiger/test/evergreen.yml lines 7780-7839

## Purpose

This chunk is part of WiredTiger's Evergreen CI build-variant matrix. It covers the task list at the end of the `amazon2023-arm64-msan` variant, the full `amazon2023-arm64-ubsan` variant, and the beginning of the `amazon2023-stress-nonstandalone` variant.

The chunk's main purpose is to decide which compile, example, make-check, format, cppsuite, csuite, and stress tasks run on Amazon Linux 2023 ARM64 hosts for sanitizer and non-standalone coverage:

- The MSAN tail runs production compile permutations, C examples, a MemorySanitizer-specific format workload, regular `make check` with cppsuite/long-running/disagg exclusions from the surrounding variant expansions, and a daily long-running csuite pass.
- The UBSAN variant configures a Clang UBSan build with tcmalloc disabled, then runs compile permutations, C example tests, pull-request-scale format/disaggregated format tests, `make check`, and the all-in-one C++ suite task.
- The non-standalone stress variant configures `WT_STANDALONE_BUILD=0`, enables tcmalloc, and starts a broad stress task set covering normal format stress buckets, disaggregated stress, abort/recovery stress, and C++ suite stress tasks.

This is CI orchestration, not WiredTiger runtime storage-engine logic. The source file is nevertheless high-impact because these build variants are part of the project's automated signal for compiler/runtime undefined behavior, sanitizer compatibility, disaggregated-storage format behavior, non-standalone embedding, and ARM64-specific coverage.

## Important APIs, Types, and Functions

The "APIs" in this range are Evergreen YAML constructs and WiredTiger Evergreen functions/tasks:

- `buildvariants` entries define CI platforms. The chunk includes `amazon2023-arm64-ubsan` and opens `amazon2023-stress-nonstandalone`; lines 7780-7792 are the task list from the preceding `amazon2023-arm64-msan` build variant.
- `name` is the Evergreen build-variant or task identifier. Examples in this chunk include `amazon2023-arm64-ubsan`, `amazon2023-stress-nonstandalone`, `compile`, `make-check-test`, and `cppsuite-default-all`.
- `display_name` is the human-facing Evergreen/Spruce name. The variants in this chunk display as `Amazon2023 ARM64 UBSAN` and `Amazon2023 ARM64 Stress tests (Non-standalone)`.
- `run_on` selects Evergreen distro aliases. The UBSAN variant defaults to `amazon2023.3-arm64-small`; heavy tasks override to `amazon2023.3-arm64-large`. The non-standalone stress variant defaults to `amazon2023.3-arm64-large`.
- `expansions` inject variables consumed by common functions. Here they set `CMAKE_PRESET`, `CMAKE_BUILD_TYPE`, `CC_OPTIMIZE_LEVEL`, `ENABLE_TCMALLOC`, `num_jobs`, and `NONSTANDALONE`.
- `tasks` lists concrete tasks or tag selectors. Plain names such as `compile` reference task definitions. Dotted names such as `.stress-test-1` and `.cppsuite-stress-test` are Evergreen task-tag selectors that expand to all tasks carrying the matching tag.
- Per-task `distros` overrides run selected work on larger hosts. In this chunk, `make-check-test` and the MSAN `csuite-long-running` run on `amazon2023.3-arm64-large`.
- Per-task `batchtime` throttles expensive work. The MSAN long-running csuite task is batched once per day with `batchtime: 1440`; the non-standalone C++ suite stress selector starts with `batchtime: 720`, meaning a 12-hour batching window.

Important referenced tasks and functions:

- `compile`, `compile-production-disable-shared`, and `compile-production-disable-static` each run `get project`, `compile wiredtiger`, artifact upload, and cleanup. The production-disable variants pass CMake flag bundles that exercise static/shared library configurations.
- `examples-c-production-disable-shared-test` and `examples-c-production-disable-static-test` compile with the corresponding library-mode flags and run `make check directory` for `examples/c`.
- `make-check-test` runs `get project`, `compile wiredtiger`, then `make check all`; `make check all` invokes CTest with label `^check$`, parallelism from `${num_jobs}`, and any variant-level `${ctest_extra_args}`.
- `format-msan-test` compiles and runs the format test script using `CONFIG.msan` for 10 minutes with smaller row/operation bounds.
- `format-stress-pull-request-test` is a 10-minute pull-request-scale format stress run.
- `format-stress-test-disagg-leader-pull-request-1`, `format-stress-test-disagg-follower-pull-request`, and `format-stress-test-disagg-switch-pull-request-1` exercise disaggregated format workloads in leader, follower, and switch modes.
- `cppsuite-default-all` fetches compile artifacts and runs the C++ suite runner from `wiredtiger/cmake_build/test/cppsuite` with `./run -C 'debug_mode=(cursor_copy=true)' -l 2`.
- `csuite-long-running` recompiles WiredTiger and runs CTest for long-running csuite labels with `ctest_extra_args: -L long_running -j ${num_jobs}`.
- `.stress-test-1` through `.stress-test-4` select tagged six-hour `format-stress-test-*` tasks and associated recovery stress buckets.
- `.stress-test-disagg` selects the longer disaggregated stress task family, including leader, follower, switch, and data-validation variants.
- `format-abort-recovery-stress-test` runs format with abort/recovery mode (`-a`) for 30 minutes and extends its task timeout to allow recovery to finish.
- `.cppsuite-stress-test` selects C++ suite stress tasks such as background compact long, operations stress, history-store cleanup stress, burst inserts stress, bounded cursor stress, and reverse split stress.

## Control Flow

Evergreen expands this YAML declaratively. For each build variant, it applies variant-level expansions, schedules tasks listed under `tasks`, and substitutes expansion variables into the task command functions.

For the MSAN tail, the control flow is inherited from the preceding `amazon2023-arm64-msan` variant. That surrounding variant sets `CMAKE_PRESET: linux-clang`, `CMAKE_BUILD_TYPE: -DCMAKE_BUILD_TYPE=MSan`, disables tcmalloc, disables compressor libraries that would not be MSAN-instrumented, forces `-O0`, and sets `ctest_extra_args: -LE "cppsuite|long_running|disagg"`. The task list in this chunk then:

1. Builds the normal and production library-mode configurations.
2. Runs C example tests against both production library-mode configurations.
3. Runs the MSAN-specific format task.
4. Runs `make-check-test` on a large ARM64 host, with the variant's CTest exclusions preventing cppsuite, long-running, and disaggregated labels from running under the main make-check pass.
5. Schedules `csuite-long-running` separately on a large ARM64 host once per day to recover the long-running coverage excluded from `make-check-test`.

For `amazon2023-arm64-ubsan`, Evergreen first applies the UBSAN expansions:

- `CMAKE_PRESET: linux-clang` selects the Clang CMake preset.
- `CMAKE_BUILD_TYPE: -DCMAKE_BUILD_TYPE=UBSan` causes common test setup to export `UBSAN_OPTIONS` and `TESTUTIL_UBSAN`.
- `CC_OPTIMIZE_LEVEL: -DCC_OPTIMIZE_LEVEL=-O0` keeps sanitizer traces easier to debug than Clang's default debug optimization behavior.
- `ENABLE_TCMALLOC: 0` avoids preloading tcmalloc in sanitizer test shells.
- `num_jobs` is calculated from `/proc/cpuinfo`.

The UBSAN task flow then builds the project in three library configurations, validates C examples for static/shared permutations, runs normal format stress plus disaggregated pull-request smoke coverage, runs `make-check-test` on the larger distro, and finishes with `cppsuite-default-all`. Unlike the MSAN variant, this chunk does not exclude cppsuite from `make-check-test` and explicitly includes the default all-C++ suite task.

For `amazon2023-stress-nonstandalone`, the chunk starts a stress variant. Variant-level expansions enable tcmalloc and pass `NONSTANDALONE: -DWT_STANDALONE_BUILD=0` into compile/configure paths. The task list starts with `compile`, then uses tag selectors to fan out to four format stress buckets, disaggregated stress, abort/recovery stress, and C++ suite stress tasks. The actual selected tasks are defined earlier in the same YAML file through anchors and tags; Evergreen resolves the dotted entries at configuration generation/scheduling time.

## State and Persistence Behavior

This YAML does not persist WiredTiger database state itself. It defines CI state: variant identity, expansion variables, task scheduling, host class, batching, and artifact flow.

The most important state passed through this chunk is Evergreen expansion state:

- `CMAKE_BUILD_TYPE` determines compile-time sanitizer instrumentation and is later consumed by `PREPARE_TEST_ENV`. When it contains `UBSan`, the common setup exports `UBSAN_OPTIONS="$COMMON_SAN_OPTIONS:print_stacktrace=1"` and `TESTUTIL_UBSAN=1`; when the previous MSAN variant contains `MSan`, setup exports `MSAN_OPTIONS` and `TESTUTIL_MSAN=1`.
- `ENABLE_TCMALLOC` controls whether `PREPARE_TEST_ENV` sets `LD_PRELOAD` to `TCMALLOC_LIB/libtcmalloc.so`. Sanitizer variants set it to `0`; the non-standalone stress variant sets it to `1`, making a missing tcmalloc library a task failure.
- `CC_OPTIMIZE_LEVEL=-O0` is a variant-level compile option that persists into compile commands and changes binary debuggability and runtime performance.
- `num_jobs` persists into CTest and script invocations. In these variants it is computed from ARM64 host CPU count.
- `NONSTANDALONE=-DWT_STANDALONE_BUILD=0` changes the build contract for the stress variant, exercising WiredTiger as a non-standalone component rather than the default standalone build shape.
- The MSAN surrounding `ctest_extra_args` persist into `make-check-test`, explicitly excluding cppsuite, long-running, and disaggregated CTest labels from that task.

Artifact persistence is indirect. Compile tasks upload build artifacts; tasks that depend on `compile` or use `fetch artifacts` reuse those outputs. C++ suite tasks archive `wiredtiger/cmake_build` after removing unrelated directories, upload a tarball to the `build_external` S3 bucket under a path containing `${build_variant}`, `${revision}`, `${task_name}`, and `${build_id}`, and then remove the checkout while preserving the saved test exit code. Global post hooks also upload stack traces, stdout/stderr, stats files, format configs, model workloads, and artifacts.

Test database directories are created and destroyed by the referenced task scripts rather than by this chunk. For example, format tasks create workload homes, wtperf/csuite/cppsuite tasks produce their own test output, and cleanup/post hooks remove workspace state after task completion.

## Dependencies and Integration Points

This chunk integrates with Evergreen, WiredTiger's CMake/test wrappers, and several task families defined elsewhere in `test/evergreen.yml`:

- Evergreen distro aliases: `amazon2023.3-arm64-small` and `amazon2023.3-arm64-large` must exist and provide the expected ARM64 Amazon Linux 2023 environment.
- Common Evergreen functions: `setup environment`, `get project`, `compile wiredtiger`, `upload artifact`, `cleanup`, `fetch artifacts`, `make check all`, `make check directory`, `format test script`, `format test disagg`, `cppsuite test run all`, and C++ suite archive/upload helpers.
- Toolchain integration: `linux-clang`, `/opt/mongodbtoolchain/v5/bin`, CMake presets, Clang sanitizer runtimes, CTest, `bc`, `/proc/cpuinfo`, and shell scripts under `test/evergreen`.
- Sanitizer integration: common setup derives sanitizer environment variables from `CMAKE_BUILD_TYPE`. UBSAN uses `UBSAN_OPTIONS` with stack traces; MSAN uses `MSAN_OPTIONS` and avoids uninstrumented compression libraries in the surrounding variant.
- TCMalloc integration: the non-standalone stress variant requires the compile/configure path to build or download `TCMALLOC_LIB/libtcmalloc.so`, because `PREPARE_TEST_ENV` preloads it when `ENABLE_TCMALLOC=1`.
- CMake configuration anchors: `compile-production-disable-shared`, `compile-production-disable-static`, examples production tests, format stress tasks, recovery stress tasks, and cppsuite tasks depend on earlier YAML anchors for library-mode flags, built-in extension flags, and stress task command templates.
- CTest label integration: `make-check-test` runs the `check` label with variant-level inclusions/exclusions; `csuite-long-running` explicitly includes `long_running`.
- Disaggregated-storage test integration: the leader/follower/switch format tasks use `CONFIG.disagg` and `disagg.mode=*` arguments. Some anchored definitions force `num_jobs: 1` for PALite limitations, so variant-level `num_jobs` does not always determine actual parallelism.
- Tag selector integration: dotted task names must match task tags exactly. If tags drift, the stress variant can silently lose or gain task coverage.

## Risks and Edge Cases

- Lines 7780-7792 are only the tail of the MSAN variant. Interpreting them without the immediately preceding expansions would miss the critical MSAN behavior: Clang preset, `-DCMAKE_BUILD_TYPE=MSan`, compression-library disables, tcmalloc disabled, `-O0`, and CTest exclusions.
- Sanitizer variants deliberately disable tcmalloc. Accidentally enabling tcmalloc under MSAN or UBSAN could introduce allocator instrumentation gaps or make failures harder to interpret.
- UBSAN does not include the MSAN `ctest_extra_args` exclusions in this chunk. Adding exclusions or removing `cppsuite-default-all` would materially change UBSAN coverage.
- The `num_jobs` expression uses shell, `grep`, and `bc` against `/proc/cpuinfo`. If an ARM64 host image lacks `bc` or changes CPU reporting, task parallelism expansion can fail or produce unexpected values.
- `make-check-test` is overridden to the large distro in sanitizer variants. Removing that override risks timeouts or resource failures on small ARM64 hosts.
- `csuite-long-running` is daily-batched in MSAN because it is expensive. Lowering `batchtime` increases CI cost; raising it reduces sanitizer signal frequency for long-running tests.
- `CC_OPTIMIZE_LEVEL=-O0` trades runtime for clearer sanitizer debugging. Removing it can make sanitizer traces less actionable and may change optimizer-sensitive undefined behavior exposure.
- The non-standalone variant sets `WT_STANDALONE_BUILD=0` but still selects broad stress tags. Any task that assumes standalone-only binaries, build products, or extension paths can fail specifically under this variant.
- Enabling tcmalloc in the non-standalone stress variant means tests depend on `LD_PRELOAD`. Missing or incompatible `libtcmalloc.so` fails early in test setup, while subtle allocator differences can change stress-test timing and memory behavior.
- Dotted task selectors are broad. Adding a new task tagged `stress-test-1`, `stress-test-disagg`, or `cppsuite-stress-test` automatically adds it to this variant; removing/renaming a tag automatically removes coverage.
- Disaggregated format tasks are sensitive to PALite/PALI limitations and force serial execution in some definitions. Raising parallelism through variant-level changes may not affect those tasks, while overriding task vars incorrectly could violate the PALite single-job assumption.
- The chunk ends at the `batchtime` line for `.cppsuite-stress-test`. The following lines likely complete that task entry or variant; this document should be reconciled with the next chunk before making conclusions about the full non-standalone variant.

## Test Signals

Useful signals produced or protected by this chunk include:

- UBSAN runtime findings from `make-check-test`, examples, format stress, disaggregated format, and C++ suite default-all runs, including stack traces via `UBSAN_OPTIONS`.
- MSAN runtime findings from the preceding variant's task tail, especially the `format-msan-test`, `make-check-test` with unsafe labels excluded, and daily `csuite-long-running` pass.
- Compile/link signals from normal, disable-shared, and disable-static production build tasks on Amazon Linux 2023 ARM64.
- C example compatibility signals under production static/shared build modes.
- CTest health signals from `make-check-test`, with large-host resource behavior visible through task success, timeouts, and output-on-failure logs.
- Long-running csuite sanitizer signal via `csuite-long-running`, scheduled separately from ordinary make-check to avoid mixing expensive labels into every MSAN run.
- Disaggregated-storage smoke signals in UBSAN from leader, follower, and switch pull-request format tasks.
- Non-standalone build and stress signals from compiling with `-DWT_STANDALONE_BUILD=0`, then running format stress, recovery stress, disaggregated stress, and cppsuite stress under that build mode.
- Artifact/debug signals from global post hooks and cppsuite-specific archive/S3 upload paths, including core dumps, stack traces, stdout/stderr, stats, format configs, model workloads, and archived C++ suite build/test state.
- Scheduling/cost signals through `batchtime`: daily MSAN long-running coverage and 12-hour batching for non-standalone cppsuite stress coverage.
