# sources/test-tools/kdevops/.github/workflows/config-tests.yml

Purpose: GitHub-hosted workflow that validates kdevops configuration generation and Linux A/B setup in containers without provisioning real infrastructure.

Important APIs/types/functions: triggers on push to `main` and `ci-testing/**`, pull requests to `main`, and manual dispatch. Environment variables define GHCR image naming. Jobs are `build-kdevops-containers`, `linux-ab-config-tests`, and `quick-config-validation`.

Control flow: the first job builds Debian testing, Fedora latest, and openSUSE Tumbleweed containers with Ansible/build dependencies, smoke-runs `make mrproper`, pushes images to GHCR, and exposes image tags as outputs. `linux-ab-config-tests` runs `make check-linux-ab` in each built image. `quick-config-validation` runs a matrix of defconfigs (`blktests_nvme`, `xfs_reflink_4k`, `lbs-xfs`, `linux-ab-testing`) across the same distros, verifies `.config` and `.extra_vars_auto.yaml`, manually generates container-safe core files (`.kdevops.depcheck`, `extra_vars.yaml`, `ansible.cfg`, `hosts`), and asserts they exist.

State/persistence behavior: builds and pushes transient container images tagged by commit SHA, writes Dockerfiles in the workflow workspace, and generates kdevops config artifacts inside job containers.

Dependencies/integration: uses `actions/checkout@v4`, `docker/login-action@v3`, GHCR package permissions, Docker build/run, and kdevops make targets. It depends on package manager names across Debian/Fedora/openSUSE.

Risks/test signals: echo strings include emoji/non-ASCII but shell behavior is otherwise straightforward. Output image steps are conditional per matrix row, so downstream jobs depend on those outputs being set correctly. Test signals are successful container pushes and config file existence checks across all matrix combinations.
