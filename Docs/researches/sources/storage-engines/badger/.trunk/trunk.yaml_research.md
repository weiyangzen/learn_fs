# sources/storage-engines/badger/.trunk/trunk.yaml

Purpose: central Trunk configuration for Badger linting, formatting, runtime, and hooks.

Important data: pins Trunk CLI `1.25.0`, uses the official plugin source at `v1.7.4`, enables Go runtime `1.25.5`, ignores generated `pb/*.pb.go`, and enables linters/security tools including two golangci-lint variants, Trivy, Renovate, actionlint, Checkov, gofmt, markdownlint, OSV scanner, image optimizers, shell tools, trufflehog, and yamllint. Actions include announce, pre-push checks, pre-commit formatting, and upgrade notification.

State and persistence: influences local developer hooks and CI lint output. Dependencies are Trunk plugin availability and runtime downloads. Risks: overlapping golangci-lint versions can produce duplicated or inconsistent findings; pinned runtime versions can drift from `go.mod`; security scanners may be noisy without tailored ignores. Test signals are `trunk check`, reusable workflow output, and pre-commit/pre-push behavior.
