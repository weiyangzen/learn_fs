# sources/distributed-fs/tahoe-lafs/misc/simulators/hashbasedsig.py

## Purpose

This exploratory simulator searches parameter combinations for a hash-based signature scheme combining GMSS-like Merkle layers, HORS leaf signatures, and generalized Winternitz signatures under size and CPU-cost limits.

## Important APIs, Types, and Functions

Global constants define hash length, signature-count security target, byte/cost limits, hash block parameters, and cycles per byte. Math helpers include `lg`, `ln`, `ceil_log`, `ceil_div`, `floor_div`, `compressions`, and `sum_powers`. `make_candidate` computes Mcycle costs and filters candidates. `calculate` searches `T`, `q`, Winternitz base `B`, and tree costs for one `(K, K1, K2)` combination. `search` precomputes efficient mixed binary/ternary Merkle tree shapes, scans candidate ranges, bins by cost, and prints Pareto-like best rows.

## Control Flow

The script prints global constraints, then `search()` iterates hash lengths. For each length it garbage-collects, precomputes tree shape costs up to `K_max`, loops over `K`, `K2`, and `K1`, calls `calculate`, filters candidates into cost bins, selects smallest signatures per nearby cost bin, sorts by signature size/cost, and prints rows that improve signing or verification cost.

## State, Dependencies, Integration, Risks, and Tests

State is CPU-heavy in-memory candidate lists and stderr progress. Dependencies are only stdlib math/gc/sys. Integration is research/design, not production Tahoe runtime. Risks include huge runtime, floating-point approximations for security probabilities, hard-coded search ranges, Python 2/3 differences from `pow` and print behavior mostly handled, and no unit tests. Test signals should target helper arithmetic, candidate filtering, small bounded `calculate` cases, and deterministic output with reduced ranges.
