# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/mymath/mymath.go

Purpose: small math helper package plus unique timestamp generation for test IDs.

Important APIs/state: package channels `query` and `timestamp` feed a goroutine that returns `time.Now()` then sleeps 1100 ms. `GetTimeStamp` formats `YYYYMMDDHHMMSS`. Also exports `MinInt`, `MaxInt`, `MaxIntSlice`, and `MinIntSlice`.

Control flow: timestamp requests serialize through an unbuffered channel, ensuring generated second-level timestamps are spaced far enough apart to avoid duplicates. Slice min/max return an error on empty input.

Integration points: LTM and KCS main handlers use `GetTimeStamp` for generated test IDs; GCP quota code uses min/max helpers.

Risks and test signals: timestamp generation intentionally throttles concurrent requests, which limits request admission rate. `MinIntSlice` returns error text saying `MaxIntSlice`. Tests cover blocked and unblocked timestamp timing.
