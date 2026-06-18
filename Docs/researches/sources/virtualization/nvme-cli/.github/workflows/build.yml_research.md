# File Research: sources/virtualization/nvme-cli/.github/workflows/build.yml

- Purpose: main CI build matrix for nvme-cli and libnvme integration.
- Triggers: push and pull request to `master`, plus manual dispatch.
- Coverage: builds Debian/Fedora/Tumbleweed containers with GCC/Clang and debug/release modes; separately builds libnvme, cross targets, fallback shared libraries, muon minimal static, Makefile static, musl, no-fabrics, Alpine, distro-style split builds, and Windows MSYS2 UCRT64.
- Key implementation: most Linux jobs run `scripts/build.sh`; cross jobs use GHCR cross containers and QEMU setup; Windows installs MSYS2 packages and runs the same build script.
- Artifacts: failing jobs upload Meson logs from `.build-ci/meson-logs`.
