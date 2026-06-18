# sources/distributed-fs/tahoe-lafs/integration/test_vectors.py

## Purpose
Verifies deterministic Tahoe capability generation against stored test vectors for combinations of convergence secrets, ZFEC parameters, plaintext samples, segment size, and object formats.

## Important APIs, Types, and Functions
`test_convergence` validates 16-byte convergence secrets. `test_capability` parametrizes over `vectors.capabilities.items()`, reconfigures Alice, uploads data with `util.upload`, and compares the capability string. `skiptest_generate` is a disabled helper for regenerating vectors. `generate` is an async generator that iterates cases, reconfigures ZFEC, customizes mutable formats, uploads, and yields `(case, cap)`.

## Control Flow
For each vector case, Alice is restarted if needed with `(happy=1, required, total)`, the case convergence secret, and case segment size. Data is uploaded in the requested CHK/SSK format, and the resulting cap must exactly match the stored expected value. The generator constructs a Cartesian product from parameter lists and incrementally rewrites the vector YAML through `vectors.save_capabilities`.

## State and Persistence
Tests mutate Alice's share configuration and convergence secret. The skipped generator can persist new vector data to `integration/vectors/test_vectors.yaml` if deliberately enabled.

## Dependencies and Integration Points
Depends on vector model/parameters modules, stored vector YAML exposed by `vectors.capabilities`, `attrs.evolve`, pytest-twisted async bridging, `integration.grid.Client`, and `util.upload`.

## Risks
The exact-capability assertion is intentionally brittle and will catch any cryptographic, encoding, segment-size, or serialization change. The generator path appears more fragile than the test path because it calls `upload(alice.process, ...)` while `util.upload` expects an object with a `.process` attribute in current usage.

## Test Signals
Signals include convergence-secret shape validation and exact equality between generated and known capability strings for all slow vector cases.
