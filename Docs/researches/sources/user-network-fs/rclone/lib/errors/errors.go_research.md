# sources/user-network-fs/rclone/lib/errors/errors.go

Source read signal: reviewed complete local file (74 lines, sha256 9b93d102a6aebc67).

Purpose: Implements generic traversal of error chains across old `Cause`, modern `Unwrap`, multi-error `Unwrap() []error`, and common stdlib structs with an `Err` field.

Important APIs/types/functions: Public `WalkFunc` and `Walk`; private interfaces `causer`, `wrapper`, and `multiWrapper`.

Control flow: `Walk` invokes the callback for the current error and stops if it returns true. It recursively walks multi-wrapper children, otherwise follows `Cause`, `Unwrap`, or reflectively extracted `Err` fields, breaking if the next error is deeply equal to the previous one.

State and persistence behavior: Stateless traversal; no mutation of errors.

Dependencies and integration points: Uses `reflect`. `pacer.IsRetryAfter` depends on `Walk` to find nested retry metadata, and other packages can use it for mixed error-chain compatibility.

Risks and test signals: Reflection on unexported or unusual `Err` fields can panic if interface extraction is invalid, though the intended targets are exported stdlib fields. Recursive multi-error walking lacks cycle detection beyond the single-chain DeepEqual guard.
