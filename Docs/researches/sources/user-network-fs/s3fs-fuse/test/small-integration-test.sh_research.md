# sources/user-network-fs/s3fs-fuse/test/small-integration-test.sh

## Purpose
Top-level Automake test script that prepares cache/SSE test state, starts S3Proxy, mounts s3fs with selected option sets, and invokes `integration-test-main.sh`.

## Important APIs, Types, And Control Flow
Uses strict bash options, sources `integration-test-common.sh` and `test-utils.sh`, creates `/tmp/s3fs-cache`, sets fake/ensure diskfree values, generates SSE key material, exports cache/diskfree variables, and builds `FLAGS`. With `ALL_TESTS`, it runs many option combinations: cache/diskfree/xattr/parent-stat, content-md5, noobj-cache disabled, small stat cache, no copy API, no multipart, SigV2, SigV4, small multipart copy threshold, and streamupload. Without `ALL_TESTS`, it runs only `sigv4`. It starts S3Proxy, creates the bucket if needed, loops mount/test/unmount for each flag, and stops S3Proxy.

## State And Persistence
Creates/removes cache directory, writes `/tmp/ssekey*`, creates or reuses a test bucket, mounts/unmounts s3fs repeatedly, and leaves downloaded S3Proxy/pjdfstest artifacts managed by the common harness.

## Dependencies And Integration Points
Depends on the common harness, OpenSSL, base64, S3 helper functions, helper binaries, and the full integration suite. It is the single `TESTS` entry in `Makefile.am`.

## Risks And Test Signals
Default coverage is intentionally small (`sigv4` only). `ALL_TESTS` is expensive and option-dependent. Some SSE options are present but disabled because S3Proxy lacks support. Passing this script is the main automated integration signal for a build.
