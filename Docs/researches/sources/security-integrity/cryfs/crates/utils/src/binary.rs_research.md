# sources/security-integrity/cryfs/crates/utils/src/binary.rs

Purpose: binary serialization/deserialization helpers around `binrw` with strict stream completion and custom field codecs.

Important APIs/types/functions: `BinaryReadExt` adds `deserialize_from_complete_stream` and `deserialize_from_file`; `BinaryWriteExt` adds `serialize_to_stream` and `serialize_to_file`. Helpers encode/decode bool, `HashMap`, null-terminated nonzero byte strings, `NonZeroU32`, and `SystemTime` via internal `TimeSpec`.

Control flow: reads use little endian, improve unexpected EOF context, and call `ensure_stream_is_complete` to reject trailing bytes. File reads return `Ok(None)` on not-found. Writes create/overwrite files and use buffered writers.

State/persistence: serialization writes files when requested; otherwise operates on caller streams. HashMap serialization order is iteration-dependent.

Dependencies/integration: depends on `anyhow`, `binrw`, `itertools`, std IO/path/time, and test-only helper module.

Risks: strict EOF handling is good for integrity but rejects concatenated streams. `read_null_string` requires a null terminator and rejects EOF-terminated strings. `read_timespec/write_timespec` call `stream_position().unwrap()` when constructing custom errors.

Test signals: broad unit tests cover success and failures for stream length, files, bool validation, hashmap lengths, null strings, nonzero integers, and timespec overflow/short data.
