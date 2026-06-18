# sources/security-integrity/fsverity-utils/programs/test_compute_digest.c

Purpose: This test program validates `libfsverity_compute_digest()` against known data, edge cases, metadata callback behavior, and invalid parameter handling.

Important APIs and functions: It supplies read callbacks, known file contents or synthetic buffers, expected digest vectors, and callback implementations for Merkle tree size, tree blocks, and descriptor reporting.

Control flow and state: Tests construct parameter structs, call the library, compare returned digest bytes and callback records, and check negative errno results for invalid inputs. State is local test buffers and allocated digest objects.

Dependencies and integration points: Exercises public library API, hash algorithms, descriptor layout, and metadata callbacks without requiring kernel fs-verity support.

Risks and test signals: This is a high-value compatibility suite because digest changes affect every fs-verity consumer. Signals include exact known-answer hashes, empty-file behavior, salt/block-size variants, callback offsets, and validation failures.
