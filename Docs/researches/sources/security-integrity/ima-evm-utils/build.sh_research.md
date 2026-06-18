# sources/security-integrity/ima-evm-utils/build.sh

## Purpose
Shared CI build-and-test driver for ima-evm-utils. It configures compiler flags, optional OpenSSL 3 build paths, native/i386/cross variants, kernel-test enablement, install prefix, and test log handling.

## Important APIs, Types, And Functions
- `title` prints section headers.
- `log_exit` dumps logs and exits with normalized status.
- `CC`, `CFLAGS`, `PREFIX`, `COMPILE_SSL`, `VARIANT`, `TESTGROUP`, and `TST_*` environment variables control behavior.
- Runs `./autogen.sh`, `./configure`, `make -j$(nproc)`, `make install`, `openssl list -providers`, and `make check`.

## Control Flow
Under CI it enables shell tracing, redirects stderr to stdout, and mounts securityfs. It sets paths, handles OpenSSL override, chooses variant flags, disables kernel tests unless requested, builds, installs, skips checks for cross-compile, and interprets test exit 77 as warning/skip.

## State And Persistence
Mutates the source tree with generated Autotools files and build outputs, installs into `$PREFIX`, and may mount `/sys/kernel/security` in CI.

## Dependencies And Integration Points
Depends on package scripts having installed build dependencies, optional OpenSSL under `/opt/openssl3`, and tests producing standard Automake logs.

## Risks And Edge Cases
Unset variables are used under `/bin/sh`; CI usually supplies them, but local runs may need explicit defaults. Mounting securityfs requires privileges.

## Test Signals
Signals are successful configure/build/install, provider listing, green `make check`, accepted skip handling, and `tests/make check_logs` on success.
