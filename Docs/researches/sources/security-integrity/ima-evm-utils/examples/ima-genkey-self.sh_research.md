# sources/security-integrity/ima-evm-utils/examples/ima-genkey-self.sh

## Purpose
User-facing wrapper that creates a self-signed EVM/IMA signing key.

## Important APIs, Types, And Functions
- Sources `./functions` from the examples directory.
- Defaults to `rsa:2048` unless a key algorithm argument is supplied.
- Displays help and calls `ima_gen_signing_key_selfsigned`.

## Control Flow
The wrapper performs minimal argument handling and delegates certificate/key generation to the shared shell library.

## State And Persistence
Writes `x509_evm.genkey`, `x509_evm.der`, `privkey_evm.pem`, and `pubkey_evm.pem` style artifacts.

## Dependencies And Integration Points
Depends on OpenSSL and the algorithm mapping in `functions`.

## Risks And Edge Cases
The EC public-key extraction typo in `functions` can affect this wrapper for `prime256v1`. Private key output is unencrypted.

## Test Signals
Exit status is the self-signed generator result.
