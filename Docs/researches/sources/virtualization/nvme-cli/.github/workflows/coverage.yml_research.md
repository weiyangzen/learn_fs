# File Research: sources/virtualization/nvme-cli/.github/workflows/coverage.yml

- Purpose: manual Codecov upload workflow.
- Trigger: `workflow_dispatch`.
- Key behavior: runs only for `linux-nvme/nvme-cli`, builds coverage with `scripts/build.sh -p`, then uploads `coverage.xml`.
- Policy: `continue-on-error: true` and `fail_ci_if_error: false`, so coverage upload does not block CI.
