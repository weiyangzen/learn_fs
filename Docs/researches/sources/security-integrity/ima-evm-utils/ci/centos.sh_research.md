# sources/security-integrity/ima-evm-utils/ci/centos.sh

## Purpose
Installs the ima-evm-utils build and test dependencies inside a CentOS/Fedora-family CI container. It normalizes CI-provided compiler and TPM/TSS selections into distro package names before the shared `build.sh` runs.

## Important APIs, Types, And Functions
- `CC` is mandatory and is expanded to include `gcc` when helper tools require it.
- `TSS` is translated to distro-specific IBM TSS or tpm2-tss development packages.
- `yum` installs compiler, autotools, OpenSSL, keyutils, xattr/attr, docbook/asciidoc, TPM simulator, pkcs11, and filesystem utility packages.

## Control Flow
The script validates required environment, rewrites `TSS`, refreshes package metadata when needed, installs a broad dependency set, and optionally runs helper installers for components that are missing or not packaged.

## State And Persistence
It mutates the container package database and may install files under `/usr`, `/usr/local`, or helper-script defaults. No repository source files are modified.

## Dependencies And Integration Points
Integrated by GitHub Actions and legacy Travis through the derived `ci/centos.sh` launcher. It feeds the later autoconf, make, and test phases in `build.sh`.

## Risks And Edge Cases
Package names are distro-sensitive; stale package names, missing optional repos, or unavailable `tss2-devel or tpm2-tss-devel` packages can fail CI before source compilation. Several optional installs are deliberately best-effort, so coverage can vary by image.

## Test Signals
A successful run is signaled indirectly by the next CI stage reaching `./configure`, `make`, and `make check` on CentOS/Fedora-family.
