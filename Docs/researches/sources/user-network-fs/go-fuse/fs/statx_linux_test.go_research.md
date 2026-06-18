## sources/user-network-fs/go-fuse/fs/statx_linux_test.go

Purpose: Linux test for `statx` forwarding and timestamp/attribute fidelity through loopback mounts.

Important APIs/types/functions: `lstatxPath` calls `unix.Statx` with `AT_SYMLINK_NOFOLLOW`. `clearStatx` masks volatile fields before comparison. `TestStatx` compares statx results from the original path and mounted path.

Control flow: the test creates loopback-backed filesystem state, gathers `Statx_t` from both sides, normalizes fields that are known to differ, and checks equality.

State and persistence: backing files live in temp directories. The mount should not synthesize persistent statx values beyond what loopback returns.

Dependencies and integration: targets Linux `NodeStatxer`/raw `STATX` plumbing and `fuse.Statx.FromStatx` conversion.

Risks and test signals: catches field loss in statx conversion, masking, or raw opcode dispatch. It is Linux-only and depends on kernel statx support.
