# sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/tailing_reads_test.go

## Purpose

Tests tailing reads from an open handle while an unfinalized zonal object is remotely appended at the same generation. It validates that file size and sequential reads advance as appendable object content grows.

## Important APIs, control flow, and dependencies

`unfinalizedObjectTailingReads` sets up a mounted suite, creates a per-test directory and file name, and uses `client.CreateUnfinalizedObject`, `os.OpenFile`, `readFile.Stat`, `client.AppendableWriter`, and `operations.CloseFileShouldNotThrowError`. `TestTailingRead` reads initial content, then loops twice: fetch object attrs and generation, open an appendable writer for that generation, write random data, close, sleep past the two-second metadata TTL, stat the open handle, and read the newly appended bytes.

## State, persistence, dependencies, and integration points

The object generation should remain stable across appends. The read handle remains open, so the test probes whether gcsfuse refreshes size for an existing handle after metadata TTL expiry and can continue reading from the current file offset.

## Risks and test signals

Risks include fixed sleeps causing flakiness, metadata cache not expiring, remote append changing generation unexpectedly, and kernel-reader differences. Signals are exact initial read content, updated `Stat` size after each append, exact appended data read from the same handle, and successful close.
