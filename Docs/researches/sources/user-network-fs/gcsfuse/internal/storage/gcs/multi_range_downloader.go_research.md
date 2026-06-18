# sources/user-network-fs/gcsfuse/internal/storage/gcs/multi_range_downloader.go

## Purpose
This file defines a narrow interface over the Go storage client's multi-range downloader so gcsfuse code can depend on a mockable abstraction.

## Important APIs and Control Flow
`MultiRangeDownloader` has `Add(output io.Writer, offset, length int64, callback func(int64, int64, error))`, `Close`, `Wait`, `Error`, and `GetHandle`. `Add` schedules range downloads into caller-provided writers, `Wait` blocks for pending ranges, `Close` releases downloader resources, `Error` returns aggregate state, and `GetHandle` exposes a resume/read handle byte slice.

## State, Dependencies, and Integration
The interface stores no state itself. It depends only on `io`. `gcs.Bucket.NewMultiRangeDownloader` returns this interface, fake tests exercise it heavily, and mocks implement it indirectly through bucket mock return values.

## Risks and Test Signals
Because this is an interface, behavior depends entirely on implementations. Callback ordering, concurrent `Add`, when errors surface, and `Close` versus `Wait` semantics must stay aligned with the underlying Go storage client and the expectations in `bucket_tests.go`.
