# sources/user-network-fs/smblibrary/Utilities/Cryptography/CRC32.cs

Purpose: `CRC32` implements a `HashAlgorithm` for standard CRC-32 and exposes convenience static computations.

Important APIs/types/functions: constants `DefaultPolynomial` and `DefaultSeed`; constructors for default/custom polynomial; overrides `Initialize`, `HashCore`, `HashFinal`, `HashSize`; static `Compute` overloads; `UPDC32` incremental update helper.

Control flow: initializes a 256-entry lookup table, iterates bytes updating the CRC, complements the final hash, and returns big-endian hash bytes for `HashAlgorithm`.

State and persistence behavior: instance state includes current `hash`, `seed`, and `table`; `defaultTable` is cached statically after first default initialization.

Dependencies and integration points: inherits `System.Security.Cryptography.HashAlgorithm`; can be used in stream hashing APIs.

Risks: `CalculateHash` loops `for (i = start; i < size; i++)`, treating `size` as an end index rather than `start + length`; this is correct only when `start` is zero and is a likely bug for `HashCore` with nonzero start. `defaultTable` initialization is not synchronized, though races produce equivalent data.

Test signals: standard CRC32 vector for `123456789`, HashAlgorithm incremental block tests with nonzero start offsets, custom polynomial tests, and `UPDC32` consistency.
