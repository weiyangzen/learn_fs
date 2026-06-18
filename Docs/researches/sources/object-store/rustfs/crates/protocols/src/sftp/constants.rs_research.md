# sources/object-store/rustfs/crates/protocols/src/sftp/constants.rs

Purpose: This file groups the SFTP implementation's named constants: backend error substrings, POSIX modes, protocol identifiers, S3 API limits, SSH transport tuning, watchdog timing, read-directory caps, backend deadlines, write retry settings, and read-cache memory bounds.

Important APIs and types: `s3_error_codes` names S3-code fragments such as `NoSuchKey`, `NoSuchBucket`, `AccessDenied`, and `NoSuchUpload`. `http_error_codes` names numeric fragments. `posix` provides `POSIX_DIR_MODE`, `POSIX_FILE_MODE`, and test-only `POSIX_TYPE_MASK`. `protocol` defines SFTP version 3 and subsystem name `sftp`. `limits` defines constants such as `MAX_READ_LEN`, handle bounds, keepalive values, handshake and wedge watchdog timers, SSH channel/event buffer sizes, S3 multipart/copy limits, shutdown drain timeout, root listing and READDIR page caps, backend operation timeout bounds, commit-write retries/backoff, and read-cache window/total-memory bounds.

Control flow: There is no executable control flow. Constants are imported by SFTP config, server, driver, directory, errors, and attribute code to keep numeric policy in one place.

State and persistence behavior: No state or persistence. Constants determine runtime resource ceilings and wire-visible behavior.

Dependencies and integration points: `posix` composes modes from crate-wide path constants. `SftpConfig` uses handle, timeout, part-size, and cache bounds. Directory listing uses `ROOT_LISTING_MAX_ENTRIES` and `READDIR_PAGE_MAX_KEYS`. Error mapping uses the S3/HTTP fragments. Server code uses SSH buffer, keepalive, handshake, shutdown, and watchdog constants.

Risks: Many constants are protocol or AWS contract values and should not drift without compatibility review. Operational bounds affect memory pressure: the upper handle count combined with part-size can imply very high worst-case session memory. Error classification by substring is pragmatic but can misclassify unusual backend error text. SFTP protocol version is fixed at 3, so later draft semantics require separate implementation work.

Test signals: Indirect tests assert POSIX mode values, config resolver bounds, read-cache sentinels, and driver behavior around errors/timeouts/listing. No direct tests live in this constants file.
