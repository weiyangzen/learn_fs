# sources/security-integrity/ima-evm-utils/ci/debian.cross-compile.sh

## Purpose
Variant setup script for Debian cross-compilation CI rows.

## Important APIs, Types, And Functions
- `ARCH` is mandatory and mapped to `aarch64`, `powerpc64le`, or `s390x` gcc triplets.
- `dpkg --add-architecture $ARCH` enables target packages.
- Installs target gcc, target libc headers, `dpkg-dev`, and `libssl-dev`.

## Control Flow
The script validates the requested architecture, adds it as a Debian foreign architecture, updates apt metadata, and installs cross toolchain pieces needed before the generic Debian dependency script and `build.sh` run.

## State And Persistence
Mutates dpkg architecture state and apt package database in the CI container.

## Dependencies And Integration Points
Integrated by CI when `VARIANT=cross-compile`; `build.sh` later derives `--host` from `CC`.

## Risks And Edge Cases
Only arm64, ppc64el, and s390x are supported. Other ARCH values fail immediately.

## Test Signals
Pass signal is availability of the cross compiler and target headers for configure.
