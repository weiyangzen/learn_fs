
# sources/security-integrity/ima-evm-utils/src/utils.h

## Purpose
`utils.h` declares the shared utility functions used by ima-evm-utils source files.

## Important APIs, Types, And Functions
It includes `ctype.h` and `sys/types.h`, then declares `get_cmd_path()`, `hex_to_bin()`, and `hex2bin()`.

## Control Flow
There is no runtime control flow in the header. It exposes utility contracts for command lookup and hex decoding.

## State And Persistence
The header itself is stateless. Implementations read process environment and input buffers.

## Dependencies And Integration Points
It is included by `utils.c`, TPM backends, and code paths needing hex conversion. It keeps utility prototypes separate from libimaevm's larger ABI header.

## Risks
The header does not document buffer ownership or exact parse semantics, so callers must know that `hex2bin()` returns `-1` on invalid hex and that `get_cmd_path()` writes into caller-owned storage.

## Test Signals
Indirect coverage comes from the same code paths as `utils.c`.
