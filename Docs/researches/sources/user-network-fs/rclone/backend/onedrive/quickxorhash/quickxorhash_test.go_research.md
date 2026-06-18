# sources/user-network-fs/rclone/backend/onedrive/quickxorhash/quickxorhash_test.go

Purpose: verifies the QuickXorHash implementation against fixed vectors and hash interface behavior.

Important APIs: `testVectors` holds base64-encoded inputs and expected base64 hash outputs for many sizes, including empty input, small inputs, block-boundary inputs, and larger random-looking payloads. `TestQuickXorHash` checks one-shot `Sum`. `TestQuickXorHashByBlock` checks incremental `New().Write().Sum()` with block sizes from 1 to 512. `TestSize`, `TestBlockSize`, `TestReset`, and the `hash.Hash` assertion cover interface shape. `BenchmarkQuickXorHash` measures 1 MiB buffers.

Control flow: each vector is decoded, hashed, and compared to the decoded expected output. The block test loops through the same vectors while writing input in varying chunk sizes, making it the main guard for `Write` remainder and circular data behavior. The benchmark resets the hasher each iteration, writes a 1 MiB random buffer, and calls `Sum`.

State and persistence behavior: no persistent state; tests use random bytes only in the benchmark. The reset test records the zero hash, mutates the hasher with one byte, resets, and expects the zero hash again.

Dependencies and integration points: uses standard `crypto/rand`, `encoding/base64`, `fmt`, `hash`, and `testing`, plus `testify` `assert` and `require`. It tests only the local quickxor package, but its correctness protects OneDrive hash comparisons.

Risks: expected vectors are embedded in source and are the authority for compatibility. Benchmark randomness is not deterministic, but benchmark output is not a correctness gate. The vectors include multiline base64 strings, so accidental formatting damage can break decoding.

Test signals: strong algorithmic coverage for one-shot and incremental writes; no direct fuzzing or collision/security claims, which is appropriate for a non-cryptographic service hash.
