# sources/user-network-fs/s3fs-fuse/test/integration-test-common.sh

## Purpose
Shared shell harness for starting/stopping S3Proxy, optional Chaos HTTP Proxy, pjdfstest, and an s3fs mount for integration tests.

## Important APIs, Types, And Control Flow
Sets defaults for `S3_URL`, `S3_ENDPOINT`, credentials, bucket, S3Proxy versions/hashes, and proxy settings. `retry` repeatedly evaluates commands. `start_s3proxy` downloads/verifies S3Proxy and Chaos HTTP Proxy if missing, generates a self-signed cert for HTTPS, starts Java services, waits for ports, and downloads/builds pjdfstest. `start_s3fs` selects auth mode, optional valgrind, proxy, macOS/FUSE-T, certificate, cache/stat options, starts s3fs in foreground with logging prefixing, captures PID, and waits for the mount. `stop_s3fs`, `stop_s3proxy`, and `common_exit_handler` tear down processes and mounts.

## State And Persistence
Creates credentials permissions, mount directories, downloaded binaries, `/tmp/keystore.*`, pjdfstest sources/build outputs, pid files, exported environment variables, background Java/s3fs processes, and mounted FUSE state.

## Dependencies And Integration Points
Depends on bash, curl, sha256sum, keytool, Java, S3Proxy, Chaos HTTP Proxy, pjdfstest autotools, FUSE/fusermount3 or macOS umount, awk, grep, `/proc/mounts`, and `test-utils.sh` helpers used by callers. It is sourced by `small-integration-test.sh`.

## Risks And Test Signals
Network downloads are pinned by hash but still depend on external availability. `eval` in `retry` is flexible but risky. Port waits assume fixed ports. Cleanup trap does not stack automatically. Successful mount/start/stop across Linux and macOS is the foundational signal for all integration tests.
