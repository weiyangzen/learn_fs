# sources/object-store/rustfs/crates/filemeta/src/error.rs

Purpose: central error type and `Result` alias for file metadata operations.

Important APIs/types/functions: `pub type Result<T> = core::result::Result<T, Error>`. `Error` covers storage-style states (`FileNotFound`, `FileVersionNotFound`, `VolumeNotFound`, `FileCorrupt`, `DoneForNow`, `MethodNotAllowed`, `Unexpected`) and wrapped codec/runtime failures (`Io`, rmp serde encode/decode, raw rmp read/write errors, UTF-8, time range, UUID parse). `Error::other` wraps arbitrary errors through `std::io::Error::other`. `is_io_eof` detects `Error::Io(UnexpectedEof)`.

Control flow and conversions: `From<std::io::Error>` maps `UnexpectedEof` to the sentinel `Unexpected`; other IO errors stay in `Io`. `From<Error> for std::io::Error` converts `Unexpected` back to `UnexpectedEof`, preserves `Io`, and wraps other variants as `Other`. MessagePack, UTF-8, time, UUID, and marker errors are stringified into stable enum variants. Manual `PartialEq` and `Clone` preserve comparability for IO errors by kind/message.

State and persistence: no persistent state. The enum is part of the public API and shapes how metadata parse failures propagate through storage callers.

Dependencies and integration: integrates `thiserror`, `std::io`, `rmp`, `rmp-serde`, `time`, and `uuid`. `DoneForNow` is used internally as a controlled early-stop sentinel in metadata scanning.

Risks: mapping raw `UnexpectedEof` into `Unexpected` means `is_io_eof` does not detect EOFs after conversion through `From<std::io::Error>`. Stringifying third-party errors loses structured details but makes clone/equality simpler. `Error::other` wraps source errors as IO `Other`, which can blur domain boundaries.

Test signals: unit tests cover conversion, `other`, clone, equality, display strings, rmp/time/uuid/marker conversion, EOF helper behavior, IO round-trip preservation, error-kind handling, and wrapped message retention.
