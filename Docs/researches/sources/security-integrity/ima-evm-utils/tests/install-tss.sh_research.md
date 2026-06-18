
# sources/security-integrity/ima-evm-utils/tests/install-tss.sh

## Purpose
This helper builds and installs IBM TSS for TPM 2.0 PCR-reading test support.

## Important APIs, Types, And Functions
It clones `https://github.com/kgoldman/ibmtss`, runs `autoreconf -i`, configures with `--disable-tpm-1.2 --disable-hwtpm`, builds, installs with sudo, then removes the source tree.

## Control Flow
The script uses `set -ex` and stops on failed commands.

## State And Persistence
It installs IBM TSS libraries/tools into the system prefix selected by the upstream configure script. The cloned `ibmtss` directory is removed afterward.

## Dependencies And Integration Points
It depends on Git, autotools, compiler tools, Make, and sudo. `pcr_ibmtss.c` and `pcr_tsspcrread.c` test paths rely on IBM TSS components.

## Risks
The remote branch is unpinned. System installation can affect other TPM tooling. Hardware TPM is disabled in configure, which is appropriate for simulator-focused CI but not full hardware testing.

## Test Signals
Successful installation provides TPM library/tool support for measurement and boot aggregate tests.
