<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/lib.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/lib.rs

## Purpose
This is the library entry point for rcloud. It exposes the main internal modules for integration tests and potential external reuse.

## Important APIs
The file publicly exports `api`, `config`, `metrics`, and `vm`.

## Control Flow and Integration
There is no runtime logic. `tests/api_tests.rs` imports `rcloud::api::handlers::health` through this library entry point, while `src/main.rs` declares its own modules for the binary.

## State, Persistence, and Dependencies
No state is stored here. The dependency surface is the public module graph.

## Risks and Test Signals
The library exports broad internal modules, which is convenient for tests but makes future refactors more visible to downstream users. Compile-time testing is the main signal; if any public module fails to compile, both library and tests fail.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/lib.rs -->
