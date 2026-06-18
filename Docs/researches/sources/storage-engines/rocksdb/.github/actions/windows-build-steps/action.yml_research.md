<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/windows-build-steps/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/windows-build-steps/action.yml

Purpose: Composite Windows CI build/test action for RocksDB and RocksJava under Visual Studio.

Important APIs/types/functions: inputs `suite-run` and `run-java`; uses `microsoft/setup-msbuild`, `hendrikmuhs/ccache-action`, PowerShell ccache config, Chocolatey Liberica JDK install, Snappy source build, CMake configure with `WIN_CI`, `PORTABLE`, `SNAPPY`, `XPRESS`, `JNI`, MSBuild, `build_tools\run_ci_db_test.ps1`, Java `ctest`, and final ccache stats.

Control flow: configure msbuild/cache, install dependencies, build Snappy, configure RocksDB, build solution with high parallelism, run requested C++ suite shards, optionally run Java tests, and show cache stats.

State and persistence behavior: creates `thirdparty`, Snappy build outputs, CMake `build`, ccache content, and test outputs in the workspace. Nothing is committed.

Dependencies and integration points: used by PR and nightly Windows jobs with different `CMAKE_GENERATOR` and `CMAKE_PORTABLE` values. Integrates with Visual Studio, Chocolatey, CMake, CTest, Snappy, Java/JNI, and RocksDB PowerShell test runner.

Risks: many external tools and URLs can fail. The action uses fixed paths like `C:\a\rocksdb\rocksdb` for ccache base dir. `/m:32` can exceed actual CPU capacity but expects cache hits. Each PowerShell command needs explicit `$LASTEXITCODE` handling, so missing checks could hide errors.

Test signals: successful MSBuild, `run_ci_db_test.ps1`, optional Java CTest, and ccache stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/windows-build-steps/action.yml -->
