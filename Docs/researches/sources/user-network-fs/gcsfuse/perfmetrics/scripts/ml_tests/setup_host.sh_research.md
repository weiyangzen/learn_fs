<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/setup_host.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/setup_host.sh

## Purpose
Prepares a VM host for ML container workloads by installing Ops Agent, Docker, NVIDIA drivers, and NVIDIA container tooling.

## Important APIs, Types, And Functions
Single shell entry point taking `DRIVER_VERSION` as `$1`.

## Control Flow
Adds Google Ops Agent repository, installs common apt packages, configures Docker apt repo and Docker Engine, downloads and runs the Tesla NVIDIA driver installer, adds NVIDIA container toolkit repository, installs toolkit, and restarts Docker.

## State And Persistence Behavior
Mutates apt sources/keyrings, installs system packages, downloads a driver `.run` file, installs kernel driver components, and restarts Docker.

## Dependencies
Ubuntu apt, curl, gpg, Docker upstream repo, NVIDIA driver and container toolkit repositories.

## Integration Points
Supports ML perf/checkpoint workloads that need containerized GPU runtime.

## Risks And Edge Cases
Assumes Ubuntu, x86_64 Tesla driver URL, sudo privileges, and compatible kernel headers. It uses deprecated `apt-key` for one key path.

## Test Signals
No tests in this subset; validation is implicit through successful host provisioning.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/setup_host.sh -->
