
# sources/security-integrity/ima-evm-utils/tests/install-swtpm.sh

## Purpose
This helper builds and installs IBM's software TPM server for TPM-dependent tests.

## Important APIs, Types, And Functions
It clones `https://github.com/kgoldman/ibmswtpm2`, builds under `ibmswtpm2/src`, and copies `tpm_server` to `/usr/local/bin/`, using `sudo` only when necessary.

## Control Flow
With `bash -ex`, it selects `SUDO` based on write permission to `/usr/local/bin`, clones, builds, copies, and returns.

## State And Persistence
It creates an `ibmswtpm2` source tree and installs `tpm_server` into `/usr/local/bin`.

## Dependencies And Integration Points
It depends on Git, Make, compiler tools, and permissions for `/usr/local/bin`. TPM PCR tests can use the installed simulator with IBM TSS.

## Risks
The cloned source is unpinned. The script does not clean the source tree after install. System installation can overwrite an existing `tpm_server`.

## Test Signals
Presence of `/usr/local/bin/tpm_server` enables software TPM-backed boot aggregate and measurement tests.
