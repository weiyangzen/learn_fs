# sources/user-network-fs/rclone/lib/structs/structs.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/structs/structs.go -->
## sources/user-network-fs/rclone/lib/structs/structs.go

Purpose: reflection utilities for copying public struct fields across similar structs or applying default values without copying unexported internals.

Important APIs and control flow: `SetFrom(a, b)` expects pointers to structs, iterates fields of `b`, finds a same-named field in `a`, and assigns it when both values are valid/settable and `b`'s field type is assignable to `a`'s field type. `SetDefaults(a, b)` expects same-kind struct pointers and copies every settable field by index from `b` to `a`.

State, dependencies, and integration: stateless helpers depending on `reflect`. Integration points include generated cloud SDK structs and `http.Transport`-like structs where unexported mutexes prevent simple struct assignment.

Risks and test signals: functions panic if called with non-pointers, nil pointers, or non-struct elements. `SetDefaults` assumes same layout/type and does not check assignability by name. Tests cover copying defaults from `http.DefaultTransport` and name/type-filtered copying in both directions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/structs/structs.go -->
