# sources/storage-engines/tikv/components/test_pd/src/mocker/retry.rs

## Purpose
This file contains mockers for PD client retry behavior. One mocker produces transport-style retryable errors before eventual success; another returns PD header errors that should not trigger the same retry path.

## Important APIs, Types, And Functions
`Retry` stores a retry interval count and atomic call counter. `is_ok` returns true only when the count is nonzero and divisible by `retry`; otherwise it sleeps for `REQUEST_RECONNECT_INTERVAL` and returns false. It overrides `get_region_by_id` and `get_store`, returning `Err("please retry")` until the scheduled success.

`NotRetry` stores an atomic visited flag. On the first `get_region_by_id`, it returns an OK response with header `RegionNotFound`; on the first `get_store`, an OK response with header `Unknown`; later calls return empty OK responses.

## Control Flow And State
Both mockers are stateful through atomics. `Retry` simulates repeated gRPC failures and delays to give clients time to update connections. `NotRetry` simulates server-level semantic errors carried in PD response headers, not transport errors.

## Integration Points And Risks
These mockers integrate through `PdMocker` and PD protobuf response headers. `Retry::new(0)` would panic on modulo by zero, so callers must pass a positive retry interval. Shared `NotRetry` state is reused across both methods, so invoking one method first changes the other's first-call behavior.

## Test Signals
Tests should assert retry loops recover from `Retry` errors after expected attempts and that header errors from `NotRetry` are surfaced without inappropriate reconnect retry behavior.
