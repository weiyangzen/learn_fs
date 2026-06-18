# sources/security-integrity/ima-evm-utils/build-static.sh

## Purpose
One-command static build helper for the `evmctl` binary.

## Important APIs, Types, And Functions
- Runs `gcc -static` over `src/evmctl.c` and `src/libimaevm.c`.
- Forces inclusion of `config.h`.
- Links against `crypto`, `keyutils`, and `dl`.

## Control Flow
The script directly invokes gcc without running configure or make, assuming generated config and dependencies are already present.

## State And Persistence
Writes `evmctl.static` in the current directory.

## Dependencies And Integration Points
Depends on static libc and static/linkable OpenSSL and keyutils libraries.

## Risks And Edge Cases
By bypassing Automake, it can miss conditional source selection or compiler flags from the normal build. Static linking availability varies by distro.

## Test Signals
The signal is a successfully linked `evmctl.static` executable.
