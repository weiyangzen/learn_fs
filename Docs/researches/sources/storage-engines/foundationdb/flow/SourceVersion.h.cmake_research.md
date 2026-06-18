<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/SourceVersion.h.cmake -->
# sources/storage-engines/foundationdb/flow/SourceVersion.h.cmake
- Purpose: Minimal CMake template that generates a compile-time source version macro from the current git version.
- Important APIs/types/functions: Defines `sourceVersion` as `"${CURRENT_GIT_VERSION}"`.
- Control flow: No runtime flow. CMake substitutes the variable during build configuration.
- State and persistence behavior: The generated macro embeds build provenance in binaries. It is source/build metadata, not mutable runtime state.
- Dependencies and integration points: Consumed by version-reporting and diagnostics code that needs the repository revision.
- Risks: Stale or missing `CURRENT_GIT_VERSION` produces misleading version metadata. Because this is a macro rather than typed constant, include ordering and macro collisions should be watched.
- Test signals: Build/version tests should verify the generated header contains the expected revision string and that binaries surface it where required.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/SourceVersion.h.cmake -->
