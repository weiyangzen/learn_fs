# sources/storage-engines/foundationdb/bindings/java/src/tests.cmake

Purpose: CMake include file that centralizes Java test source lists so the main build logic can consume test inventory without embedding file names inline.

Important APIs and flow: defines `JAVA_JUNIT_TESTS`, `JUNIT_RESOURCES`, `JAVA_INTEGRATION_TESTS`, and `JAVA_INTEGRATION_RESOURCES`. Unit tests are expected under `src/junit`; integration tests under `src/integration`; resource lists include helper classes such as fake transactions, library rules, database requirements, and multi-client helpers.

State and persistence: build-system variables only; no runtime state. Integration is with higher-level CMake logic for compiling/running Java binding tests. Risks include stale lists when files are added/removed, path assumptions, and this file not listing the standalone manual test classes researched in this subset. Test signal is build configuration coverage: missing entries mean tests may not compile or run in intended lanes.
