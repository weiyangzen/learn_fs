# sources/sync-backup/borg/.github/workflows/ci.yml Research

## Purpose

`ci.yml` is BorgBackup's main continuous integration and release-build workflow. It runs lint, security checks, sanitizer tests, native tox matrices, cross-OS VM tests, Windows binary/tests, and an informational SHA256 pack-id lane. On tags matching `2.*`, selected jobs build, smoke-test, attest, and upload binaries.

## Important APIs, Types, and Functions

Triggers include pushes to `master`, tags `2.*`, and pull requests to `master` touching code/config/requirement paths but excluding `docs/**`. Global concurrency cancels stale PR runs. Default permissions are read-only contents, with broader id-token/attestations permissions on jobs that attest binaries.

Jobs include `lint` using `astral-sh/ruff-action@v3`; `security` installing `bandit[toml]`; `asan_ubsan` building Borg with sanitizer flags and running pytest with `LD_PRELOAD`; `native_tests` using a dynamic JSON matrix that is smaller for PRs and broader for pushes/tags; `vm_tests` using `cross-platform-actions/action@v1.2.0` for FreeBSD, NetBSD, OpenBSD, and OmniOS; `windows_tests` using MSYS2 and PyInstaller; and `sha256_pack_id_tests` as continue-on-error tox coverage for alternate pack IDs.

## Control Flow

Most test jobs depend on `lint`. Native tests set up Python, pip/tox caches, OS packages, optional SFTP and MinIO services, locked development requirements, editable Borg installs with extras chosen from `TOXENV`, optional tag-only binary builds, provenance attestation, artifact upload, tox execution, and Codecov uploads. VM tests run OS-specific shell branches inside a cross-platform action, including package installation, filesystem setup for NetBSD xattrs, OpenSSL naming for OpenBSD, and TMPDIR relocation for OmniOS. Windows builds a venv, builds Borg/PyInstaller artifacts, uploads the binary, and runs pytest.

## State and Persistence Behavior

The workflow creates caches, build artifacts, binary artifacts, provenance attestations, coverage and test-result uploads, local service state for SSH/MinIO during jobs, and GitHub Actions artifacts. It does not write back to the repository. Tag builds produce distributable binary artifacts.

## Dependencies and Integration Points

CI integrates with GitHub Actions runners across Linux, macOS, Windows, ARM, and BSD-like VMs; Python 3.11-3.14; tox; pytest; Codecov; PyInstaller; SFTP/OpenSSH; MinIO; rclone; FUSE variants; Homebrew; MSYS2; package managers for BSD/OmniOS; and GitHub artifact/provenance attestation APIs.

## Risks and Edge Cases

The workflow has high dependency surface and long timeouts, so third-party action changes, runner image changes, package repository outages, or service startup timing can break CI. Some actions are tag-pinned rather than SHA-pinned. VM tests are `continue-on-error`, so regressions on less common platforms may not block merges. Native matrix `fail-fast: true` can stop other matrix entries after one failure, reducing signal. Direct downloads of MinIO binaries are not checksum-verified. The PR path filter excludes docs changes, so documentation build breakage from docs-only edits is not caught here.

## Test Signals

The workflow itself is the dominant test signal. Important health indicators are sanitizer failures, tox matrix pass/fail, Codecov uploads, binary smoke tests, artifact presence on tags, provenance attestation success, cross-OS VM outcomes, and canary comparison for dependency drift.
