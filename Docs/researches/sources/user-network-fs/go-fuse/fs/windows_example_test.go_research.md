## sources/user-network-fs/go-fuse/fs/windows_example_test.go

Purpose: example showing Windows-like delete semantics on a loopback filesystem by preventing unlink of open files.

Important APIs/types/functions: `WindowsNode` wraps children with `WrapChild`, intercepts `Open`, `Create`, `Release`, and `Unlink`, and tracks an `openCount`. `isBusy` checks a child node's open count before unlink. `Example_loopbackReuse` mounts a loopback root using the wrapper.

Control flow: new children are wrapped into `WindowsNode`. Open/create increments count; release decrements. `Unlink` checks for active opens and returns a busy error rather than unlinking.

State and persistence: backing data lives in the loopback directory. Open counts are in-memory per wrapper node and protected by a mutex/atomic style in the example.

Dependencies and integration: demonstrates `NodeWrapChilder`, high-level node wrappers, loopback reuse, and Windows compatibility policy atop POSIX kernel calls.

Risks and test signals: as an example, it documents a policy pattern rather than a full test. Correctness depends on balanced Release calls and wrapping every child.
