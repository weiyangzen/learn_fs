# sources/sync-backup/git-crypt/.github/workflows/release-linux-arm64.yml

Purpose: GitHub Actions workflow that builds and uploads a Linux ARM64 git-crypt binary whenever a GitHub release is published.

Important APIs/types/functions: `on.release.types: [published]`, build job on `ubuntu-22.04-arm`, upload job on `ubuntu-latest`, `actions/checkout@v3`, `actions/upload-artifact@v4`, `actions/download-artifact@v4`, and `actions/github-script@v6` calling `github.rest.repos.uploadReleaseAsset`.

Control flow: the build job checks out the repository, installs `libssl-dev`, runs `make`, and uploads the `git-crypt` binary as `git-crypt-artifacts`. The upload job depends on build, downloads that artifact, and uploads it to the release with a `linux-aarch64` asset name derived from `github.event.release.name`.

State/persistence behavior: state is carried between jobs via Actions artifacts and then persisted as a GitHub release asset. The build job has read-only contents permission; the upload job has write permission for release assets.

Dependencies/integration: integrates the repository Makefile with an ARM64 hosted runner and OpenSSL development package. Release identity is taken from the release event payload.

Risks/test signals: runner label availability and artifact naming are critical. The script imports `sha` from context but does not use it. Tests are release-dry-run/manual workflow checks: confirm ARM runner availability, binary architecture, successful artifact transfer, and uploaded asset name.
