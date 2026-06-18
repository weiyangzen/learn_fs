# sources/object-store/rustfs/crates/protocols/src/sftp/attrs.rs

Purpose: This module converts S3 bucket/object metadata into SFTPv3 `FileAttributes`, preserves selected SFTP attributes as S3 user metadata on writes, generates safe longname strings, and implements the shared `STAT`/`LSTAT`/`FSTAT` stat dispatcher for `SftpDriver`.

Important APIs and types: `s3_attrs_to_sftp` builds directory or regular-file attributes with POSIX type bits. `sftp_attrs_to_user_metadata` maps present `mtime`, `permissions`, `uid`, and `gid` into user metadata keys. `apply_user_metadata_to_sftp_attrs` overlays those keys on stat results. `timestamp_to_mtime` clamps S3 timestamps into SFTPv3 `u32` seconds. `generate_longname` sanitizes filenames and delegates formatting to `russh_sftp::protocol::File::new`. `SftpDriver::do_stat` is the async stat implementation.

Control flow: `do_stat` parses the raw path into bucket/key. Root returns default directory attributes without storage calls. Bucket paths authorize `HeadBucket`, call `head_bucket`, and return default directory attrs. Object paths authorize `HeadObject`, call `head_object`, and return file attrs using non-negative content length, clamped mtime, and optional user metadata overrides. If `head_object` reports not-found, it authorizes `ListBucket`, lists `key/` with delimiter and `max_keys=1`, and returns directory attrs if any contents or prefixes exist; otherwise it returns `NoSuchFile`.

State and persistence behavior: Attribute conversion is pure. Persistent state enters only through S3 object metadata read from `HeadObject` and metadata written elsewhere using `sftp_attrs_to_user_metadata`. There is no local cache.

Dependencies and integration points: It depends on SFTP constants, path parsing/sanitizing, SFTP error mapping, `SftpDriver` backend runners, `russh_sftp` protocol types, and `s3s::dto::ListObjectsV2Input`. SFTP handlers for stat-like operations call this shared body.

Risks: S3 user metadata values are parsed as `u32` and invalid values are silently ignored. Directory detection adds a backend listing after object miss, which is correct for pseudo-directories but can add latency. Authorization for the fallback list uses `prefix` as object context; policy semantics must agree with that. Longname safety depends on `sanitise_control_bytes` handling all control bytes clients might interpret.

Test signals: Tests cover POSIX type bits and permission triples, metadata mapping and overrides, directory/file longname prefixes, LF sanitization, timestamp clamping for pre-epoch and overflow values, and mode constant values.
