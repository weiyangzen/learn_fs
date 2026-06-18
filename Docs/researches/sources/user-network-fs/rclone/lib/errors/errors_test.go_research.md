# sources/user-network-fs/rclone/lib/errors/errors_test.go

Source read signal: reviewed complete local file (249 lines, sha256 bdac5b1c2ac7f1e5).

Purpose: Exhaustively tests `Walk` over cause, unwrap, reflected `Err`, multi-error, and callback-stop scenarios.

Important APIs/types/functions: `TestWalk` defines local error wrappers `causerError`, `wrapperError`, `multiWrapperError`, `reflectError`, and `stopError`.

Control flow: Each table case records errors visited by `Walk`; the callback stops when it sees `stopError`. Cases cover nil children, nested mixed chains, multi-wrapper fan-out, and stop behavior inside nested chains.

State and persistence behavior: Test-local error values only; no persistence.

Dependencies and integration points: Uses `errors`, `fmt`, `testing`, and `testify/assert`.

Risks and test signals: Strong behavior signal for traversal ordering and stop semantics. It does not cover cyclic multi-wrapper graphs or structs with inaccessible `Err` fields.
