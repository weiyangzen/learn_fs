
# sources/user-network-fs/rclone/lib/bucket/bucket_test.go

Purpose: validates bucket utility path semantics and cache state transitions.

Important APIs/types/functions: `TestSplit`, `TestJoin`, `TestIsAllSlashes`, and `TestCache`.

Control flow: table tests check split/join/slash edge cases. `TestCache` manually inspects cache status after marks, creates, exists errors, root operations, removes, already-deleted detection, and callback errors.

State/persistence: in-memory cache only.

Dependencies/integration: uses `testify/assert`.

Risks: tests access unexported `c.status` because they are in package `bucket`, making them precise but coupled to implementation representation.

Test signals: strong coverage for preserving multiple/trailing slashes and for avoiding repeat bucket deletion/creation calls.
