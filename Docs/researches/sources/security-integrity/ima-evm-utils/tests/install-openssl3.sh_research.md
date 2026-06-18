
# sources/security-integrity/ima-evm-utils/tests/install-openssl3.sh

## Purpose
This helper builds and installs a selected OpenSSL 3 release under `/opt/openssl3` for tests requiring newer OpenSSL features.

## Important APIs, Types, And Functions
It requires `COMPILE_SSL`, downloads the matching GitHub tag tarball, extracts it, optionally sets 32-bit flags when `VARIANT=i386`, configures OpenSSL with `no-engine no-dynamic-engine`, builds, and runs `sudo make install_sw`.

## Control Flow
The script uses `set -ex`, fails if `COMPILE_SSL` is unset, performs build/install, then removes the tarball and source directory.

## State And Persistence
Persistent effects include `/opt/openssl3` binaries and libraries installed with sudo. Temporary source and tarball artifacts are removed after installation.

## Dependencies And Integration Points
It depends on network access, `wget`, `tar`, compiler toolchain, Perl/OpenSSL build system, `sudo`, and optional 32-bit build support. `gen-keys.sh` uses `/opt/openssl3/bin/openssl` for SM2 when present.

## Risks
Downloads use `--no-check-certificate`, weakening transport verification. Installation mutates system state. Build output depends on the provided tag and host toolchain.

## Test Signals
Successful install expands coverage for OpenSSL 3-only algorithms and compatibility behavior.
