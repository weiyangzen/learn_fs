# sources/security-integrity/ima-evm-utils/ci/debian.i386.sh

## Purpose
Variant setup script for Debian i386 CI builds.

## Important APIs, Types, And Functions
- Adds the `i386` architecture.
- Installs `linux-libc-dev:i386`, `gcc-multilib`, and `pkg-config:i386`.

## Control Flow
The script enables i386 package resolution and installs the minimal multilib support needed before the generic Debian script installs architecture-qualified libraries.

## State And Persistence
Mutates dpkg architecture state and apt package database.

## Dependencies And Integration Points
Integrated by CI when `VARIANT=i386`; `build.sh` later adds `-m32` flags and i386 pkg-config path.

## Risks And Edge Cases
Assumes Debian repositories provide i386 packages for the selected image.

## Test Signals
Pass signal is successful installation of multilib compiler/pkg-config support.
