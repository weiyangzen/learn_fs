# sources/storage-engines/tikv/components/tikv_util/src/deadline.rs

## Purpose
Defines a small deadline abstraction around TiKV's coarse `Instant` plus an error helper for mapping deadline expiry into kvproto busy errors.

## Important APIs, Types, And Functions
`DeadlineError` implements `std::error::Error` and `Display` with the message `deadline has elapsed`. `Deadline` stores one `Instant` and exposes `new`, `from_now`, `inner`, `check`, `to_std_instant`, and `remaining_duration`. `set_deadline_exceeded_busy_error` fills a `kvproto::errorpb::Error` with a `ServerIsBusy` reason of `deadline is exceeded`.

## Control Flow
`from_now` adds a TiKV `Duration` to `Instant::now_coarse`. `check` first consults the `deadline_check_fail` failpoint, then compares the stored instant with current coarse time and returns `DeadlineError` when expired. `remaining_duration` uses saturating subtraction so expired deadlines report zero. `to_std_instant` translates by adding the remaining TiKV duration to `std::time::Instant::now`.

## State And Persistence
State is only the immutable deadline instant. No persistence or global mutation exists except the caller-provided protobuf error mutation.

## Dependencies And Integration
Depends on `fail`, `kvproto::errorpb`, and `super::time::{Duration, Instant}`. It integrates with request paths that need cheap deadline checks and with RPC error construction for overload/deadline signalling.

## Risks
Coarse time can make boundary behavior fuzzy by a few milliseconds. `to_std_instant` depends on the difference between coarse and standard clocks and should be used for relative timeout conversion, not exact timestamp identity. The failpoint can force errors in tests or failpoint-enabled deployments.

## Test Signals
Tests cover remaining duration for future, expired, current, and large deadlines, and verify consistency between `remaining_duration` and `check`.
