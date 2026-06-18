<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/version.go -->
# Research: sources/user-network-fs/gcsfuse/common/version.go

Purpose: centralizes the displayed gcsfuse version string.

Important APIs/types/functions: package variable `gcsfuseVersion` is set at build time with `-ldflags -X`; `GetVersion` returns the injected value or `unknown` plus the current Go runtime version.

Control flow: `GetVersion` checks for an empty injected version, substitutes `unknown`, and formats it with `runtime.Version()`.

State and persistence: no persistent state. The only mutable state is the package variable populated by build tooling.

Dependencies: `fmt`, `runtime`, and release tooling such as `tools/build_gcsfuse`.

Risks: missing linker injection makes binaries report `unknown`; callers that parse this human string must handle the appended Go version.

Test signals: release builds should assert `gcsfuse --version` contains the intended product version and Go version.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/common/version.go -->
