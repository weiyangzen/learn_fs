
# sources/security-integrity/ima-evm-utils/tests/install-mount-idmapped.sh

## Purpose
This helper builds Christian Brauner's `mount-idmapped` test utility for idmapped-mount related kernel tests.

## Important APIs, Types, And Functions
It clones `https://github.com/brauner/mount-idmapped.git` and compiles `mount-idmapped.c` into a local `mount-idmapped` binary with `gcc`.

## Control Flow
The script is linear: clone, enter directory, compile, return.

## State And Persistence
It creates a `mount-idmapped` directory and binary in the current working tree. No cleanup or installation is performed.

## Dependencies And Integration Points
It depends on Git and GCC. Kernel tests that need idmapped mounts can use the resulting binary.

## Risks
The remote repository is not pinned. The script lacks `set -e` and does not verify kernel support or required capabilities.

## Test Signals
Presence of the built binary is a prerequisite signal for idmapped mount test coverage.
