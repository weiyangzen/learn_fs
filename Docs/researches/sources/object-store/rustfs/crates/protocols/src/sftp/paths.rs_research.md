# sources/object-store/rustfs/crates/protocols/src/sftp/paths.rs

## Purpose
`paths.rs` contains pure helpers that convert client SFTP paths into bucket/key pairs while blocking traversal surprises, reserved internal directory markers, and control-byte log injection.

## Important APIs, Types, and Functions
`ensure_absolute` normalizes relative input to absolute form. `last_path_component` extracts a final component. `relative_filename` derives a single listing entry from full key plus prefix. `parse_s3_path` rejects embedded NUL/CR/LF, cleans dot segments, splits through `path_to_bucket_object`, rejects `GLOBAL_DIR_SUFFIX`, and returns `(bucket, Option<key>)`. `sanitise_control_bytes` replaces C0 controls other than tab with `?`.

## Control Flow
`parse_s3_path` rejects raw controls first, then canonicalizes with `rustfs_utils::path::clean`. Defensive `.`/`..` results collapse to root. The cleaned path is split into bucket/object, empty object becomes `None`, and internal directory marker occurrences are rejected as `BadMessage`.

## State and Persistence Behavior
The module is stateless. Its importance is consistent namespace semantics across all operations that parse paths before authorization or backend calls.

## Dependencies and Integration Points
It depends on `rustfs_utils::path`, SFTP `StatusCode`, and `SftpError`. Driver, read, directory, and write code use it; logging and SFTP name rendering use sanitization.

## Risks and Test Signals
Risks include exposing directory-marker internals, accepting CR/LF into logs, or upstream cleaning behavior changing. Tests cover parsing forms, trailing slash collapse, control and marker rejection, traversal collapse, helper edge cases, unicode preservation, and a proptest over arbitrary strings.
