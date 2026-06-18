<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ProtocolVersions.cmake -->
# sources/storage-engines/foundationdb/flow/ProtocolVersions.cmake
- Purpose: Central table of CMake variables that feed the generated protocol-version header.
- Important APIs/types/functions: Defines `FDB_PV_DEFAULT_VERSION`, `FDB_PV_FUTURE_VERSION`, downgrade bounds, masks, and every `FDB_PV_*` feature constant consumed by `ProtocolVersion.h.cmake`.
- Control flow: There is no runtime flow. CMake substitutes these variables into the header template during configuration, and compile-time assertions then validate version-shape rules.
- State and persistence behavior: Values here are source-controlled compatibility state. They determine wire compatibility and some persisted key/value encodings, so changing them has cluster upgrade/downgrade implications.
- Dependencies and integration points: Integrated by the build system and all C++ code that includes the generated `ProtocolVersion.h`. Comments document the `xyzdev` convention and patch/low-byte masking policy.
- Risks: Misordered or accidental version increments can invalidate downgrade assumptions. Reusing values is intentional for features introduced together but can be confusing. The `FDB_PV_GRPC_ENDPOINT` value is present in the CMake table but not surfaced in the observed template feature list, which should be intentional or reconciled.
- Test signals: Build configuration and compile-time static assertions validate shape. Upgrade/downgrade simulation tests and mixed-binary compatibility tests are the meaningful behavioral signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ProtocolVersions.cmake -->
