# sources/security-integrity/ima-evm-utils/.github/workflows/ci.yml

## Purpose
GitHub Actions workflow for ima-evm-utils distro CI. It runs checkpatch review, builds/caches a UML integrity kernel, and tests a large distro/compiler/TSS matrix in privileged containers.

## Important APIs, Types, And Functions
- `review` job checks generated patch files with `scripts/checkpatch.pl`.
- `build` job finds the latest linux-integrity commit, caches a UML kernel and signing key, and compiles with merged kernel configs.
- `job` matrix covers Debian i386/cross, Alpine, openSUSE, Ubuntu, Fedora, CentOS Stream, Debian testing/stable, and ALT.
- Install steps dispatch to `ci/$INSTALL[.$VARIANT].sh`; compile step calls `./build.sh` with matrix environment.

## Control Flow
Push or pull request events first run patch review. The build job prepares kernel artifacts keyed by Linux SHA and kernel config hashes. The main matrix runs in privileged containers, installs distro deps, optionally builds OpenSSL/TSS/swtpm, retrieves UML artifacts for kernel tests, prints compiler version, and builds/tests the project.

## State And Persistence
Persistent CI state is through Actions caches for `linux` and `signing_key.pem`. The workflow also mutates privileged containers with package installs and mounts.

## Dependencies And Integration Points
Depends on GitHub Actions, container images, Linux integrity git remote variables, kernel config files, package-manager scripts, tests helper installers, and `build.sh`.

## Risks And Edge Cases
Privileged containers and kernel caches are broad blast-radius CI choices. Empty optional env vars are tested with shell `[ "$VARIANT" ]` style, so shell compatibility and unset variables matter.

## Test Signals
Signals are checkpatch success, cache/build success for UML kernel, and green matrix rows through `make check` or accepted skip code handling in `build.sh`.
