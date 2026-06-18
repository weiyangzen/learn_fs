# sources/object-store/minio/cmd/erasure-errors.go

Purpose: Declares canonical erasure-layer sentinel errors for read quorum failure, write quorum failure, and no-op healing.

Important APIs/types/functions: `errErasureReadQuorum`, `errErasureWriteQuorum`, and `errNoHealRequired` are package-level `errors.New` sentinels.

Control flow and state: No runtime control flow or persistent state. These sentinels are compared/wrapped by quorum reducers, encode/decode, healing, and object error translation.

Dependencies and integration points: Used by `reduceReadQuorumErrs`, `reduceWriteQuorumErrs`, `multiWriter.Write`, `parallelReader.Read`, tests, and user-facing object error conversion.

Risks: Error identity matters because code uses `errors.Is`, direct comparison in some paths, and wrapping. Changing text or replacing sentinels can break tests and operational messages.

Test signals: Covered indirectly through encode/decode/healing tests that expect quorum and heal behavior.
