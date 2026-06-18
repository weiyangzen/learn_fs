# sources/security-integrity/ima-evm-utils/examples/ima-gen-local-ca.sh

## Purpose
User-facing wrapper that creates a local IMA/EVM CA using the shared examples function library.

## Important APIs, Types, And Functions
- Changes to its own directory and sources `./functions`.
- Defaults `keyalgo` to `rsa:2048`.
- Prints help for `-?` or `--help` and otherwise calls `ima_gen_localca`.

## Control Flow
The script normalizes execution directory, parses an optional positional key algorithm, and delegates all OpenSSL work to the shared function.

## State And Persistence
Writes local CA artifacts such as `ima-local-ca.genkey`, `.x509`, `.priv`, and `.pem` in the examples directory.

## Dependencies And Integration Points
Depends on OpenSSL and supported algorithms from `functions`.

## Risks And Edge Cases
Private CA key output is unencrypted. Positional parsing is intentionally simple and ignores extra arguments.

## Test Signals
Exit status is the generator's OpenSSL-derived status.
