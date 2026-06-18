# sources/storage-engines/wiredtiger/test/suite/test_encrypt04.py

## Purpose

Exercises mismatched connection and object encryption configurations, proving that WiredTiger either rejects incompatible encryption metadata or can still read data when the effective encryptor, key id, and secret key match.

## Important APIs, Types, and Functions

Defines `test_encrypt04`, scenario matrices for two open phases, `conn_extensions`, an overridden `setUpConnectionOpen`, deterministic `create_records`/`check_records`, and `check_okay`. It uses the `rotn` encryptor, optional `fileinclear`, and a forced `rotn_force_error` path.

## Control Flow

The test creates encrypted or clear table data under phase 1, switches instance fields to phase 2, reopens the connection, and decides success from exact equality of encryptor name, key id, and secret. On successful reopen it verifies the original records and, for changed table-level settings that remain readable, appends a second batch and verifies both batches after another reopen.

## State and Persistence Behavior

Persistence is central: records are forced through close/reopen so encrypted pages must be read from disk. Random keys and values are deterministic via seed 0. `expect_forceerror` and `got_forceerror` track whether both scenario halves selected the extension error injection path.

## Dependencies and Integration Points

Depends on `wttest`, `suite_subprocess`, `make_scenarios`, the WiredTiger extension loader, and the test-only `rotn` encryptor. It integrates with connection open configuration, table-level encryption metadata, extension customization, and stderr expectations.

## Risks and Maintenance Signals

The scenarios depend on probabilistic assumptions about wrong-key decryption not accidentally producing plausible pages, mitigated by secret keys and large randomized records. Error matching for forced decrypt failures looks for `-1000` in exception strings. It skips if extensions are unavailable.

## Test Signals

Strong signals are reopen success/failure, exact record round trips after disk flush, rejection of mismatched metadata, successful mixed clear/encrypted table behavior where allowed, and explicit assertion that forced extension errors were observed only for the intended pair.
