# sources/test-tools/fio/t/nvmept_streams.py

Purpose: destructive regression coverage for NVMe streams directives through fio `io_uring_cmd` passthrough and `dataplacement=streams`. It verifies that selected placement IDs become active stream identifiers and that invalid stream configurations fail.

Important APIs and types: `StreamsTest` builds fio command lines and validates JSON data-direction counters. `StreamsTestRR` checks expected first-N stream use for round-robin selection; `StreamsTestRand` expects the random selection not to match the first-N round-robin pattern. Device helpers `get_device_stream_ids()`, `release_stream()`, and `release_all_streams()` call `nvme dir-receive` and `nvme dir-send`.

Control flow: `main()` parses target NVMe character device, creates artifacts, resolves fio, injects filename into all tests, releases existing streams, then runs `TEST_LIST`. Each test runs fio with stream placement options. `check_result()` always attempts to release streams in a `finally` block after checking fio output, iodepth, and active stream ID state.

State and persistence: the script changes stream directive state on the device and writes normal fiotestlib artifacts. It relies on active streams being queryable after fio completion, then clears them after each case. It has no persistent state beyond artifacts and mutated test dictionaries.

Dependencies and integration points: depends on fio with NVMe passthrough, `nvme-cli`, sudo for `dir-receive`, a stream-capable NVMe device, and fiotestlib. It is designed to be invoked directly or from the fio umbrella test runner with an NVMe character device requirement.

Risks and test signals: stream selection validation can be probabilistic for random selection, as the comments note false positives are possible if random picks the same first-N set. Device setup must have streams enabled externally. Success signals are fio exit status, JSON direction counters, iodepth level when requested, exact active stream ID set for ordinary and round-robin tests, and expected non-zero failure for invalid PLIDs or missing stream IDs.
