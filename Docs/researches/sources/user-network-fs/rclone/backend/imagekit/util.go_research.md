# sources/user-network-fs/rclone/backend/imagekit/util.go

## Purpose
Provides ImageKit backend helper functions for paginated file/folder listing, name lookup, retry decisions, and path/name encoding.

## Important APIs, Types, and Functions
`getFiles`, `getFolders`, `getFileByName`, and `getFolderByName` wrap client API calls. `retryErrorCodes`, `shouldRetryHTTP`, and `Fs.shouldRetry` implement retry policy. `EncodePath`, `DecodePath`, `EncodeFileName`, and `DecodeFileName` centralize encoder usage.

## Control Flow
`getFiles` and `getFolders` loop with `Skip=len(current)` and `Limit=100`, appending results until the returned page has fewer than 100 entries. Name lookups issue a one-result filtered search query with `strconv.Quote(name)`. `shouldRetry` honors context cancellation, treats 429/503 specially with `X-RateLimit-Reset` as a millisecond retry delay, and retries generic transient errors or selected HTTP statuses.

## State and Persistence
No persistent state is maintained. Helpers return fresh slices or object pointers from ImageKit API results.

## Dependencies and Integration Points
Depends on the ImageKit client package, rclone `fs`, `fserrors`, and `pacer`. The main backend file uses these helpers for every list, object lookup, and retry-wrapped mutation.

## Risks and Edge Cases
Pagination assumes an empty or short page means completion; if ImageKit returns unstable ordering during concurrent changes, duplicates or misses are possible. `getFileByName` swallows all errors and returns nil, making some API failures indistinguishable from not found. `X-RateLimit-Reset` is interpreted as milliseconds; if ImageKit documents seconds or epoch time, retry delays may be wrong.

## Test Signals
No direct unit tests cover pagination or retry decisions. Integration tests exercise these paths indirectly.
