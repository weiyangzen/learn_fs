# sources/sync-backup/kopia/tools/tools.mk

Purpose: shared Makefile fragment for Kopia development and release tooling. It detects platform traits, computes build/version metadata, installs pinned tools into `tools/.tools`, configures npm/node, and defines helper targets for signing and checksum maintenance.

Important targets/variables: platform variables include `GOOS`, `GOARCH`, suffixes, path separators, dates, and hostnames. CI variables derive `IS_PULL_REQUEST`, `CI_TAG`, `REPO_OWNER`, and `KOPIA_VERSION`. Tool versions pin golangci-lint, checklocks, Node, Hugo, gotestsum, goreleaser, rclone, and gitchglog. Targets install tools via `go run github.com/kopia/kopia/tools/gettool` or `go install`; `all-tools`, `clean-tools`, `verify-all-tool-checksums`, and `regenerate-checksums` are key aggregate operations.

Control flow/state: Make lazily materializes binaries under `TOOLS_DIR`. It prepends the pinned Node bin directory to `PATH`, exports version strings for web UI builds, installs Windows signing tools when configured, imports macOS certificates into a temporary keychain in CI, and computes release/nightly version identifiers from tags or commit timestamps.

Dependencies/integration: integrates with `gettool`, Go, npm, GitHub Actions environment variables, Windows PowerShell tools, macOS `security`, and release scripts. Consumers include Kopia build, lint, docs, web UI, backward compatibility, and release workflows.

Risks/test signals: platform branching is broad and fragile on unusual shells. Some targets fetch `@latest` tools, reducing reproducibility. Signing targets depend on secret environment variables. Checksum verification/regeneration targets provide the strongest automated signal for downloaded tool integrity.
