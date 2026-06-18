# sources/distributed-fs/tahoe-lafs/integration/vectors/parameters.py

## Purpose
Defines the deterministic input space for capability test-vector generation: convergence secrets, segment size, plaintext object samples, ZFEC parameters, and CHK/SSK formats.

## Important APIs, Types, and Functions
`digest` and `hexdigest` wrap SHA-256. `CONVERGENCE_SECRETS` contains two 16-byte secrets. `SEGMENT_SIZE` is 128 KiB. `OBJECT_DESCRIPTIONS` contains `Sample` values chosen around literal/segment/multi-segment boundaries. `ZFEC_PARAMS` contains several `SeedParam` values including `MAX_SHARES`. `FORMATS` includes `CHK()`, `SSK(name="sdmf", key=None)`, and `SSK(name="mdmf", key=None)`.

## Control Flow
The module constructs constants at import time. `test_vectors.skiptest_generate` later forms a Cartesian product across these constants to generate vector cases.

## State and Persistence
No direct persistence, but changing any constant changes the vector-generation space and requires regenerating stored capabilities.

## Dependencies and Integration Points
Depends on `hashlib.sha256`, vector model classes, and upload format adapters from `integration.util`. Integrated by `test_vectors.py` for validation and generation.

## Risks
The chosen values encode a compatibility contract. Any change in order or content can make the stored YAML incomplete or stale. `MAX_SHARES` must be realized against each format's maximum because CHK and mutable SSK formats have different limits.

## Test Signals
Signals are convergence secret shape checks and exact capability matches across all combinations selected from these constants.
