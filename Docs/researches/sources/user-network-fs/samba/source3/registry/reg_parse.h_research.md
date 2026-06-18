# sources/user-network-fs/samba/source3/registry/reg_parse.h

## Purpose
`reg_parse.h` declares the public parser API for registration-entry `.reg` files and documents the callback event model.

## Important APIs, Types, And Functions
It defines callback typedefs for key events, value events, value-delete events, and comments. `struct reg_parse_callback` groups those handlers with opaque `data`. It declares opaque `reg_parse`, `reg_parse_new()`, `reg_parse_line()`, `reg_parse_fd()`, `reg_parse_file()`, and `reg_parse_set_options()`.

## Control Flow
Users create a parser with callbacks and feed it lines, a file descriptor, or a filename. Parsed events are delivered in file order. The implementation supplies no-op callbacks when fields are null, so consumers can ignore event categories.

## State And Persistence
The parser object is talloc-owned and transient. Persistence happens only through callbacks supplied by consumers such as the import adapter.

## Dependencies And Integration Points
The header includes standard integer and boolean types and is used by `reg_import`, `reg_format`, and registry tooling. Its comment notes that parser objects can act as `reg_format_callback` implementations because of the implementation layout.

## Risks And Test Signals
Callback signatures are the compatibility boundary. Compile tests should cover callbacks with each event type. Runtime tests should validate return-value propagation, optional callbacks, and API behavior for null file callbacks in `reg_parse_fd()`.
