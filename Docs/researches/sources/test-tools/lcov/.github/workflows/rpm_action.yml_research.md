# sources/test-tools/lcov/.github/workflows/rpm_action.yml

Purpose: GitHub Actions workflow that builds lcov RPM artifacts and publishes them on version-tagged releases.

Important APIs/types/functions: GitHub triggers for pushes to `main`/`master`, tags matching `v*`, pull requests, and manual dispatch; `permissions: contents: write`; `actions/checkout@v6`; apt packages `rpm`, `devscripts`, `equivs`, Sphinx packages, Perl, and git; `make rpms`; `$GITHUB_OUTPUT`; and `softprops/action-gh-release@v3`.

Control flow: the job checks out full history, installs build dependencies, runs `make rpms`, derives a version from the tag name or `git describe --tags --always`, and only on `refs/tags/v*` creates a GitHub release containing `*.noarch.rpm` and `*.src.rpm`.

State/persistence behavior: PR and branch runs only build artifacts in the runner workspace. Tag runs persist release assets through GitHub Releases. The source tree is not modified in CI.

Dependencies/integration: delegates package logic to the top-level lcov `Makefile`, which builds docs, tarball, and RPMs through `rpmbuild` and `rpm/lcov.spec`. Requires enough git history for version derivation.

Risks/test signals: `contents: write` is needed only for release creation, so non-tag runs still carry broader permissions than required. The `ubuntu-latest` runner may shift over time and affect package availability. Signals are successful `make rpms`, expected RPM filenames in the workspace, and release upload success for `v*` tags.
