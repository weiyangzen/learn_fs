# `sources/test-tools/fio/.github/workflows/qemu.yml`

Purpose: Runs fio integration tests inside a QEMU guest with emulated storage configurations, especially NVMe passthrough/protection information, FDP, trim verification, and zoned block device tests.

Important jobs and settings: Triggered manually and on a daily schedule. The `qemu-guest` job uses Ubuntu 22.04, Debian 12 guest image, SSH/scp environment variables, and a matrix of configurations with QEMU device options, guest test commands, and extra packages.

Control flow: The job checks out the repo, creates a source tarball, creates a guest image, builds/installs QEMU, creates a backing `nvme0.img`, starts a VM with matrix-specific devices, transfers source into the guest, installs dependencies, builds fio, optionally dumps NVMe namespace info, then runs the matrix test command over SSH.

State and persistence: Creates guest disk image, NVMe backing image, source tarball, installed QEMU, and a long-running VM for the job duration. Test output is held in Actions logs.

Dependencies and integration: Uses the local composite actions in `.github/actions`, fio test scripts under `t/`, `nvme-cli`, `sg3-utils`, SSH, KVM, and QEMU storage device support.

Risks and test signals: Scheduled VM tests are resource-heavy and sensitive to QEMU, kernel, KVM, and guest image behavior. The same `nvme0.img` backing name is reused across configurations within independent matrix jobs. Test signals include guest build success, NVMe identify output, and pass/fail of targeted fio test scripts.
