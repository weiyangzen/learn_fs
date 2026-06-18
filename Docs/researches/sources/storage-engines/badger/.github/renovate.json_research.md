# sources/storage-engines/badger/.github/renovate.json

Purpose: configures Renovate for dependency update automation.

Important data: the config extends `local>dgraph-io/renovate-config`, sets `rangeStrategy` to `widen`, disables Renovate handling of the Go toolchain through both `matchPackageNames` and `matchDepNames`, and lists `go` under `ignoreDeps`.

State and persistence: it is GitHub repository automation configuration; outputs are Renovate PR behavior rather than code artifacts. Dependencies are Renovate's JSON schema and the local Dgraph Renovate preset. Risks: depending on an external local preset can make behavior opaque in this repository; disabling Go updates means `go.mod` toolchain bumps rely on manual or separate processes. Test signals include Renovate config validation, Trunk renovate linting, and verifying that Go version changes are not proposed automatically.
