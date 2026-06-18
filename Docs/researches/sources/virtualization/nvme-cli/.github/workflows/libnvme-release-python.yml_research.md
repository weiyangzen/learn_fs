# File Research: sources/virtualization/nvme-cli/.github/workflows/libnvme-release-python.yml

- Purpose: builds and publishes libnvme Python source distributions.
- Triggers: push to `master`, any tag push, and manual dispatch with optional tag input.
- Jobs: builds release sdist, builds dev/test sdist, uploads branch builds to TestPyPI, and uploads tagged release builds to PyPI.
- Dev versioning: derives `BASE_VERSION.devREV` from latest tag and commit count, patches `meson.build`, commits the CI-only bump, then builds sdist.
- Release gate: PyPI upload only for `refs/tags/v*` in `linux-nvme/nvme-cli` and only if tag matches the release regex.
- Note: uses deprecated `::set-output` syntax in the tag-check step.
