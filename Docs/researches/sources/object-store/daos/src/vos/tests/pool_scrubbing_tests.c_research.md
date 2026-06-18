# sources/object-store/daos/src/vos/tests/pool_scrubbing_tests.c

## Purpose
Cmocka integration tests for VOS pool checksum scrubbing. They verify that the scrubber detects corrupted checksummed data, respects lazy/timed modes, handles concurrent aggregation/deletion, and triggers target drain when corruption exceeds threshold.

## Important APIs, types, and functions
- `ms_between_periods_tests()` validates scrub pacing helper math.
- `struct sts_context` owns a test VOS pool/container, scrub context, csummer, callbacks, sizes, and expected rc.
- Setup helpers create pool/container, initialize CRC16 csummer, write/fetch VOS data, corrupt payloads after checksum calculation, and configure `scrub_ctx`.
- Test cases cover single values, arrays with 1/2/4 recxs, multiple epochs/akeys/objects, overlapping extents, dkey/container deletion races, drain threshold, and lazy-mode transition.

## Control flow
Each test uses `sts_setup` to initialize VOS under `/mnt/daos/vos_scrubbing.pmem`, writes data via `vos_obj_update`, optionally corrupts the data buffer after checksum generation, calls `vos_scrub_pool`, then verifies later `vos_obj_fetch` either succeeds or returns `-DER_CSUM`/`-DER_NONEXIST`. Some tests inject yield/sleep callbacks that aggregate or punch data during scrubbing.

## State and persistence behavior
Persistent state is a temporary VOS pool file/container plus VOS object records containing checksum metadata. Corruption is persisted by writing payload bytes that no longer match the stored checksum. Scrub context tracks current pool/container/object/key/epoch traversal and corruption count. Teardown closes/destroys the pool and csummer.

## Dependencies and integration points
Depends on DAOS checksum APIs, VOS object update/fetch/punch/aggregate/scrub APIs, server scrub structures, cmocka, DAOS test utilities, and the self VOS instance initialized in `main`. It exercises real VOS storage rather than pure mocks, with callbacks standing in for pool/container lookup and target drain.

## Risks and edge cases
Tests are environment-sensitive because they use `/mnt/daos` and create a 1 GiB SCM file by default. Race-style tests rely on callback timing. Fetch immediately after a corrupted update is expected to succeed before scrubbing, so changing checksum verification timing would alter assumptions. Some duplicate test labels could make filtering ambiguous.

## Test signals
Signals include expected `-DER_CSUM`, `-DER_NONEXIST`, `-DER_SHUTDOWN`, drain callback count, no hang when lazy mode changes to timed, and successful fetches for uncorrupted/covered/current data.
