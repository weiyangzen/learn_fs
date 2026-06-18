
# sources/security-integrity/ima-evm-utils/tests/install-fsverity.sh

## Purpose
This helper installs `fsverity-utils` from source for tests that need fs-verity digest/signature tooling.

## Important APIs, Types, And Functions
It runs `git clone https://git.kernel.org/pub/scm/fs/fsverity/fsverity-utils.git`, builds with `CC=gcc make -j$(nproc)`, and returns to the parent directory.

## Control Flow
The script is linear: clone, `cd`, build, `cd ..`.

## State And Persistence
It creates an `fsverity-utils` source/build directory in the current working directory. It does not install into a system prefix or clean up after itself.

## Dependencies And Integration Points
It depends on network access, Git, GCC, Make, and CPU count via `nproc`. Kernel fs-verity tests and `sign_hash --veritysig` workflows benefit from the built utilities.

## Risks
The script tracks the remote default branch rather than a pinned revision, so results can change over time. It lacks `set -e`, so some failures may continue until `cd` or make errors surface.

## Test Signals
Successful build enables fs-verity-related kernel tests and sigv3/fs-verity digest signing paths.
