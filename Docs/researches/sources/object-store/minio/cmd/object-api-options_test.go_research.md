# sources/object-store/minio/cmd/object-api-options_test.go

## Purpose
This file provides focused unit coverage for object-attribute option parsing in `getAndValidateAttributesOpts`, currently limited to how `x-amz-object-attributes` header values are split and deduplicated.

## Important APIs, types, and functions
`TestGetAndValidateAttributesOpts` initializes `globalBucketVersioningSys`, constructs `httptest` requests and response recorders, and calls `getAndValidateAttributesOpts`. It asserts the resulting `ObjectOptions.ObjectAttributes` map using `reflect.DeepEqual`. Header constants come from `internal/http`.

## Control flow
The test table covers an empty header, a single comma-delimited header line, and multiple header lines with duplicate values. For each case it builds a GET request to `/test`, assigns the case headers, calls the option parser using the MinIO metadata bucket and a test object name, and compares the parsed attribute set.

## State and persistence behavior
There is no persistent storage interaction. The only global state mutation is assigning `globalBucketVersioningSys = &BucketVersioningSys{}` so `getOpts` can query versioning state safely. The response recorder may receive error XML for invalid attribute names, but this test ignores the `valid` flag and focuses on the parsed map.

## Dependencies and integration points
The test depends on `net/http`, `httptest`, `reflect`, the object option parser, MinIO metadata bucket naming, and HTTP header constants. It integrates with the same parsing path used by GetObjectAttributes handlers, though it avoids a full HTTP handler test.

## Risks and test signals
The signal is narrow but useful: attribute parsing must trim header lines, split comma-separated values, merge repeated headers, and deduplicate duplicates. It does not assert validity filtering, API error response shape, max-parts parsing, part-number marker parsing, version ID errors, or allowed S3 attribute names. The comment explicitly states that coverage is minimal and expected to grow when the function is modified.
