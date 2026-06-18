# sources/storage-engines/rocksdb/util/build_version.cc.in

Purpose: CMake/configure-style template that becomes a C++ source file containing RocksDB build metadata, plugin registry built-ins, and version-string helpers.

Important APIs and functions: template variables define `rocksdb_build_git_sha`, `rocksdb_build_git_tag`, `HAS_GIT_CHANGES`, and `rocksdb_build_date`, choosing Git date for clean trees and build date for modified trees. Plugin externs and built-in registry entries are injected into `ObjectRegistry::builtins_`. `AddProperty` parses `name:value` strings and skips failed substitutions. `LoadPropertiesSet` creates a heap map of build properties. `GetRocksBuildProperties` returns a static unique-owned map. `GetRocksVersionAsString` formats major/minor or major/minor/patch. `GetRocksBuildInfoAsString` formats program/version and optional verbose properties.

Control flow and state: initialization is lazy through function-local static `unique_ptr`. Build properties are immutable after initialization. The generated registry map is a namespace-level static.

Dependencies and integration: includes `rocksdb/version.h`, `rocksdb/utilities/object_registry.h`, and `util/string_util.h`. It integrates with build scripts that substitute Git, build-date, and plugin placeholders.

Risks and test signals: correctness depends on substitution tooling. `AddProperty` silently skips unresolved placeholders after the colon, which avoids exposing template artifacts but can hide build metadata failures. Static initialization of `ObjectRegistry::builtins_` is global and must match registry expectations. No direct test appears in this subset; coverage is from generated builds and version-reporting tests elsewhere.
