# sources/sync-backup/kopia/internal/crypto/pb_key_derivers.go

Purpose: provides the registry and dispatch function for password-based key derivation algorithms.

Important APIs/types/functions: `passwordBasedKeyDeriver`, global `keyDerivers`, `registerPBKeyDeriver`, `DeriveKeyFromPassword`, and `supportedPBKeyDerivationAlgorithms`.

Control flow: concrete deriver files register algorithm names during init. Registration panics on duplicates. `DeriveKeyFromPassword` looks up the requested algorithm, returns an error listing supported names if absent, otherwise delegates to the deriver.

State and persistence behavior: package-global map stores derivers for process lifetime. No synchronization is used because mutation occurs during init.

Dependencies/integration: called by repository password/key setup code. Testing builds add the insecure testing algorithm.

Risks/test signals: supported algorithm list is map-order dependent, so error messages are nondeterministically ordered. No direct test listed here covers duplicate registration or unsupported algorithms.
