# sources/object-store/apache-ozone/hadoop-ozone/interface-client/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs exclusion filter for `ozone-interface-client`. It suppresses findings for generated protobuf packages rather than hand-authored code.

Important APIs/types/functions: Defines two `<Match>` rules for packages `org.apache.hadoop.ozone.protocol.proto` and `org.apache.hadoop.ozone.security.proto`.

Control flow, state, and persistence: Build-time only. It changes static-analysis reporting, not compiled artifacts or runtime state.

Dependencies and integration points: Referenced by the module's build tooling conceptually, though the client POM also sets `spotbugs.skip=true` because this module is generated-code-only. It aligns with `OMAdminProtocol.proto`, `OmClientProtocol.proto`, `OmInterServiceProtocol.proto`, and `Security.proto`.

Risks: Broad package-level exclusions can hide defects if hand-written code is later added under the generated proto packages. If package names change, generated sources may start producing SpotBugs noise.

Test signals: No runtime tests. Build signal is that generated protobuf packages are intentionally excluded from static-analysis enforcement.
