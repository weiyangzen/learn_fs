# sources/object-store/rustfs/crates/ecstore/src/client/admin_handler_utils.rs

## Purpose
Defines the simple `AdminError` type used by admin client utilities to carry a code, human-readable message, and HTTP status code.

## Important APIs, Types, and Functions
- `AdminError { code, message, status_code }` derives `thiserror::Error`, `Debug`, `Clone`, and `PartialEq`.
- `Display` renders only the message.
- `AdminError::new` constructs an arbitrary code/message/status.
- `AdminError::msg` constructs an `InternalError` with status 500.

## Control Flow and State Behavior
The type is a data container with constructors. No I/O or mutation beyond construction.

## Dependencies and Integration Points
Depends on `http::StatusCode`, `std::fmt`, and `thiserror`. It can be wrapped in `std::io::Error::other` or returned directly by admin APIs.

## Persistence
No persistence.

## Risks and Edge Cases
`Display` omits code and status, so logs or wrapped errors may lose structured context if only formatted as a string. `Default` gives an empty code/message with default status, which may be ambiguous.

## Test Signals
No inline tests. Simple tests could validate constructors and display behavior.
