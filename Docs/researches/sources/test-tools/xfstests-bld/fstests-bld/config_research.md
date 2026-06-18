# sources/test-tools/xfstests-bld/fstests-bld/config

Purpose: default source repository and version configuration for building xfstests-bld components.

Important APIs and functions: shell variables for upstream git URLs, optional repository URLs, pinned commits/tags for fio, libaio, quota, and xfsprogs, optional toolchain variables, and linker flags.

Control flow: sourced by `get-all`/`build-all`; it contains no complex logic.

State and persistence: defines the reproducible source inputs and default build flags. Local `config.custom` can override it.

Dependencies and integration: integrated by build scripts that fetch repos, check out commits, and configure cross compilation.

Risks: pinned versions can become stale against newer kernels/tests. Optional repos are commented out, so related components are skipped unless configured and present.

Test signals: `get-all` fetches expected repositories and `build-all` uses the pinned commits and linker settings.
