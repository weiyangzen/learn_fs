# sources/storage-engines/foundationdb/contrib/ddsketch_compare.py

## Purpose
Compares two DDSketch bucket distributions from JSON files using Jensen-Shannon divergence.

## Important APIs, Types, And Functions
`relative_entropy(p, q)` computes KL divergence terms while skipping zero pairs. `relative_entropy_symmetric(dd1, dd2)` normalizes bucket arrays and computes Jensen-Shannon divergence. CLI args select transaction keys, input files, and operation name.

## Control Flow
The script parses arguments, loads both JSON files, verifies matching `errorGuarantee`, extracts bucket arrays, computes divergence, and prints a similarity value where lower is more alike.

## State And Persistence
Read-only file input and stdout output. Opened JSON files are not explicitly closed.

## Dependencies And Integration
Depends on NumPy and the DDSketch JSON schema produced by FoundationDB latency tooling. Pairs with `ddsketch_calc.py` conceptually but does not import it.

## Risks
`--op` is optional in argparse but dereferenced unconditionally. Bucket arrays must have identical lengths or indexing can fail. Empty/all-zero buckets divide by zero. Skipping terms where `q[i] == 0` deviates from strict KL divergence behavior and can understate difference.

## Test Signals
Identical distributions should return 0; disjoint distributions, length mismatch, empty buckets, differing error guarantees, and missing op keys should be tested.
