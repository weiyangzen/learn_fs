# sources/user-network-fs/gcsfuse/perfmetrics/scripts/build_and_install_gcsfuse.sh

## Purpose

Builds a gcsfuse Debian package for a supplied branch or commit and installs it on the current machine for perfmetrics/e2e jobs.

## Important APIs, Types, and Functions

Accepts one positional `<branch-or-commit-id>`. Uses `dpkg --print-architecture`, Docker apt setup, `docker buildx build`, `docker run`, and `dpkg -i`. Build args include `ARCHITECTURE`, `GCSFUSE_VERSION=0.0.0`, and `BRANCH_NAME`.

## Control Flow

With `set -e`, detects architecture, installs Docker if absent or if in Kokoro, validates the argument, builds `./tools/package_gcsfuse_docker/`, copies `/packages` from the container to `$HOME/release`, and installs the generated `.deb`.

## State and Persistence Behavior

Installs Docker packages if needed, writes release artifacts under `$HOME/release/packages`, and changes the installed system `gcsfuse` package.

## Dependencies and Integration Points

Requires Ubuntu apt, sudo, curl, gpg, lsb-release, Docker buildx, package build context, and dpkg. Called by perfmetrics local tests and e2e build script.

## Risks and Edge Cases

Raw branch names are used in Docker tags and can break if they contain invalid tag characters. Assumes Ubuntu/Debian tooling. Fixed package version `0.0.0` overwrites previous artifacts and does not encode commit identity.

## Test Signals

Successful Docker build, generated `$HOME/release/packages/gcsfuse_0.0.0_${architecture}.deb`, successful `dpkg -i`, and downstream tests using the installed package.
