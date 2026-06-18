# sources/object-store/rustfs/crates/e2e_test/src/protocols/sftp_compliance.rs

Purpose: public orchestration entry points for the SFTP compliance suite. It groups numbered CMPTST cases into read-write, read-only, and standalone-server suites with shared setup where possible.

Important APIs/types/functions: constants define non-overlapping SFTP/S3 addresses for read-write and read-only suites. `test_sftp_compliance_suite` runs CMPTST-01..14 plus CMPTST-34 against one read-write server/session. `test_sftp_compliance_readonly` seeds fixtures over S3, connects to a read-only SFTP server, and runs CMPTST-15..23. `test_sftp_compliance_standalone` runs CMPTST-24..29 and 32..33, with Linux-only cases 24..26. It imports case modules and helpers from `sftp_compliance_tests`, `sftp_helpers`, and `ProtocolTestEnvironment`.

Control flow: each shared-suite entry spawns RustFS via `spawn_compliance_rustfs`, waits for the SFTP port, opens an SFTP session, executes numbered case functions in order, drops the SFTP handle, disconnects the SSH session, kills the server process, and returns the case result. The read-write suite also builds an S3 client against the paired S3 endpoint to check multipart metadata propagation for CMPTST-34. The read-only suite seeds a bucket/object through S3 because SFTP mutations are expected to fail. The standalone suite delegates to cases that each manage their own server configuration.

State and persistence behavior: shared suites create temporary RustFS processes and protocol sessions. Read-only mode starts SFTP as read-only while leaving the S3 endpoint writable for fixture setup. Standalone tests isolate state per case because they require incompatible settings such as idle timeout, read-cache window, or console disabled state.

Dependencies and integration points: integrates SFTP protocol behavior with S3 fixture setup and RustFS process spawning. Depends on `russh` disconnect semantics through helper return values, AWS S3 `ByteStream`, `anyhow`, and Linux-only system state checks in selected cases.

Risks: fixed ports 9024/9300 and 9025/9301 can conflict with other protocol tests if teardown fails. Several cases are intentionally omitted from default suite for structural/runtime reasons, so full compliance requires separate ignored entries in `sftp_compliance_tests.rs`. Teardown errors are discarded by design, so only assertion results bind outcome.

Test signals: broad SFTP regression signal for binary and zero-byte round trips, path traversal/dotdot handling, cross-bucket rename, paths with spaces, readlink/setstat shapes, implicit directories, read-only mutation rejection and read allowance, kernel/session leak checks on Linux, concurrent/pipelined operations, EOF reads, read-cache behavior, and multipart metadata propagation.
