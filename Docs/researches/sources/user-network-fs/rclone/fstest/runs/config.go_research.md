
# sources/user-network-fs/rclone/fstest/runs/config.go

Purpose: package `runs` config handling converts YAML test/backends matrices into executable `Run` records for `fstest/test_all`.

Important APIs/types/functions: `Test` describes a Go test package path and package-level flags. `Backend` describes a configured remote, backend name, feature flags, ignored tests, retry settings, extra timeout, and environment. `Config` groups tests and backends. Key methods are `Backend.includeTest`, `Backend.MakeRuns`, `NewConfig`, `Config.MakeRuns`, `FilterBackendsByRemotes`, `FilterBackendsByBackends`, and `FilterTests`.

Control flow: `NewConfig` reads and YAML-unmarshals the config. `Config.MakeRuns` computes the Cartesian product of included backends and tests. `Backend.MakeRuns` expands fast-list variants, parses `MaxFile`, applies `LocalOnly`, attaches ignore maps/env/list retry settings, and optionally appends backend name to the package path.

State/persistence: no persistent state; it reads a YAML file and mutates in-memory `Config` slices during filters.

Dependencies/integration: depends on rclone `fs.ConfigFs` to synthesize backend records for explicit remotes absent from YAML, `fs.SizeSuffix` for max file parsing, and `gopkg.in/yaml.v3`.

Risks: unknown filter names silently drop tests/backends except for remote synthesis; invalid `maxfile` logs but leaves size limit zero. Backend/test names must match source package paths exactly.

Test signals: exercised by `test_all` and indirectly by run reports; no direct unit tests in this file.
