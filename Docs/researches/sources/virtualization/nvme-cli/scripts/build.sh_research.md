# File Research: sources/virtualization/nvme-cli/scripts/build.sh

CI build orchestration script for nvme-cli.

Key elements:
- Supports Meson and Muon build tools.
- Options select build type, compiler, build tool, coverage, sanitizer setup, cross target, and valgrind setup.
- Provides Meson configs for default, musl, libdbus, fallback dependencies, cross compile, docs variants, static builds, minimal static builds, no-fabrics builds, tests, libnvme-only, and distro split build.
- Provides Muon default config and bootstrap helpers for Samurai and Muon if missing.
- Runs configure, compile, tests, optional coverage via `gcovr`, and config-specific install when defined.

Notable config behavior:
- Static/minimal static configs disable several dependencies and tests.
- `distro` first installs libnvme into the CI build prefix, then builds nvme-cli against that installed dependency.
- Sanitizer and valgrind are implemented as Meson test setups.
- Script deletes `.build-ci` before each run.

Dependencies:
- Requires git top-level discovery, Meson/Muon/Ninja/Samurai, compiler toolchains, and optional tools such as valgrind/gcovr.
