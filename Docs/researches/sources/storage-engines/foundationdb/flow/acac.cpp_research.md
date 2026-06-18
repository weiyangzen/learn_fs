<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/acac.cpp -->
# sources/storage-engines/foundationdb/flow/acac.cpp
- Purpose: Command-line decoder for ACAC actor-context dumps when FoundationDB is built with actor context instrumentation.
- Important APIs/types/functions: `loadUIDActorMapping`, `dumpActorContextTree`, `dumpActorContextStack`, `decodeClass`, and `main`; the non-ACAC build has a stub `main` that reports unsupported configuration.
- Control flow: In ACAC builds, the program parses options, recursively reads `.uid` mapping files from a build directory, optionally decodes a single class UID, otherwise reads an encoded actor context from stdin, normalizes escaped newlines, decodes it, and prints either a spawn tree or stack depending on dump type.
- State and persistence behavior: Mapping data is loaded into an in-memory `unordered_map<UID,string>`. The tool reads build artifacts and stdin and writes decoded text to stdout/stderr; it does not persist new files.
- Dependencies and integration points: Depends on `flow/ActorContext.h`, Boost program options and string algorithms, filesystem iteration, and UID mapping files produced by ACAC-enabled builds. Trace error paths in `Trace.cpp` can emit actor context strings consumed here.
- Risks: `identifierToActor.at()` throws if mappings are missing, so the build directory must match the binary that produced the dump. Recursive directory traversal can be expensive. Non-ACAC builds intentionally return failure.
- Test signals: Validation should include decoding a known class UID, tree dumps with parent/child relationships, stack/current-call dumps with `<ACTIVE>` marking, escaped newline input, missing mapping failure, and non-ACAC stub behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/acac.cpp -->
