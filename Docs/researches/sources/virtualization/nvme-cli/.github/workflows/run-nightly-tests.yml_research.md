# File Research: sources/virtualization/nvme-cli/.github/workflows/run-nightly-tests.yml

- Purpose: nightly hardware/VM regression and coverage workflow.
- Triggers: manual dispatch and daily schedule at 01:00 UTC.
- Main job: runs on self-hosted `arc-vm-nvme-cli`, checks out `linux-blktests/blktests-ci`, and uses a KubeVirt action with NVMe host devices.
- Test coverage: installs dependencies, builds mdadm from a pinned known-good commit, builds nvme-cli with coverage, runs blktests `nvme` and `md/001`, then runs nvme-cli’s own nvmetests in a privileged podman container.
- Artifacts/coverage: collects coverage XML reports and uploads them to Codecov in a follow-up job.
- Environment sensitivity: depends on `BDEV0`, host NVMe devices, custom runner, KubeVirt action, and GHCR containers.
