# sources/sync-backup/rsync/.github/workflows/macos-build.yml

Purpose: macOS build and test coverage.

Important APIs/types/functions: runs on macOS hosted runner, installs dependencies as needed, configures/builds rsync with rrsync, runs version and tests, likely includes TCP daemon coverage and artifact upload.

Control flow: path-filtered push/PR plus scheduled execution. Uses platform package manager/toolchain and standard rsync configure/make/test steps.

State and persistence: uploads built binaries/manpages for inspection.

Dependencies/integration: covers Darwin-specific APIs, filesystem metadata, terminal/signal differences, and bundled scripts.

Risks: Homebrew package churn and macOS runner image changes can cause unrelated failures; extended attribute/ACL semantics differ from Linux.

Test signals: build, suite execution, version output, and artifact upload.
