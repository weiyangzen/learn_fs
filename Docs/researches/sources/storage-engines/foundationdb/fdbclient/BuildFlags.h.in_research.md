# sources/storage-engines/foundationdb/fdbclient/BuildFlags.h.in

Purpose: This CMake-configured header template exposes build metadata as constants and a JSON string. It records compile date/time, git hash, FoundationDB version, architecture, compiler, Boost version, CMake version, ccache use, glibc version when available, and the active C++ standard.

Important APIs and types: It defines `C_VERSION_MAJOR`, `C_VERSION_MINOR`, constants such as `kDate`, `kTime`, `kGitHash`, `kFdbVersion`, `kArch`, `kCompiler`, `kBoostVersion`, `kCMakeVersion`, `kCCacheEnabled`, `kCVersionMajor`, `kCVersionMinor`, `kCppStandard`, and the function `jsonBuildInformation()`. It uses `JSONDoc` and `json_spirit`.

Control flow: At configure time, CMake substitutes placeholders like `@FDB_VERSION@`, `@CURRENT_GIT_VERSION_WNL@`, and compiler/system values. At compile time, preprocessor macros fill date, time, glibc, Boost, and `__cplusplus`. `jsonBuildInformation` creates a JSON object, sets each metadata field, formats glibc as `major.minor`, and returns pretty-printed JSON with a trailing newline.

State and persistence behavior: There is no runtime persistence. The generated header bakes build state into every binary that includes it. `__DATE__` and `__TIME__` make outputs sensitive to compile time and can affect reproducibility unless the build system controls those macros.

Dependencies and integration points: This template is consumed by the build system to generate `BuildFlags.h`. It depends on Boost version macros being available through build includes and on `fdbclient/JSONDoc.h`. The resulting JSON is typically surfaced by binaries or diagnostics that report build provenance.

Risks: Defining non-`inline` namespace-scope constants and a non-`inline` function in a header can create ODR/linkage concerns if included in multiple translation units without internal linkage expectations. Placeholder substitution must escape values appropriately for C++ string literals. Non-glibc platforms report `0.0`, which consumers must not treat as an actual libc version.

Test signals: Validation consists of successful configured builds and JSON parseability of `jsonBuildInformation()`. Useful checks assert that substituted fields are not raw `@...@` placeholders in generated artifacts and that `cpp_standard`/glibc fields match the compiler environment.
