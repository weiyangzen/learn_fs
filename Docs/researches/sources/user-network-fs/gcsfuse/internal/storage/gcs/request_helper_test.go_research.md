# sources/user-network-fs/gcsfuse/internal/storage/gcs/request_helper_test.go

## Purpose
This file tests `NewCreateObjectRequest`.

## Important APIs and Control Flow
`TestCreateObjectRequest` creates a current timestamp and table-drives three scenarios: nil source with mtime, existing source with metadata and object attributes plus mtime, and nil source without mtime. Each case calls `NewCreateObjectRequest` and compares the returned request with the expected struct using `testify/assert`.

## State, Dependencies, and Integration
The test is stateless aside from the local timestamp. Dependencies are `testing`, `time`, and `testify/assert`. The expected requests use slice-backed pointer literals for generation preconditions to compare pointer values by pointed content.

## Risks and Test Signals
The test confirms metadata maps are populated with mtime and copied source metadata. It also locks in the behavior that existing-source requests use the source object's name. It does not mutate source metadata after helper return, so map non-aliasing is not directly verified.
