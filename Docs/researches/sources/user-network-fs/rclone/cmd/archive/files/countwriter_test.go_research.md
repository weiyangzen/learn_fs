# sources/user-network-fs/rclone/cmd/archive/files/countwriter_test.go

Purpose: unit tests for `CountWriter`. It defines `stubWriter` for short/partial/error writes and validates counting semantics across normal writes, nil writer behavior, zero-length writes, partial writes with errors, short successful writes, and concurrent write/count safety.

State is in-memory only. Dependencies are `io`, `sync`, `testing`, and testify. Test signal is strong for byte accounting behavior and confirms that the counter adds exactly the `n` returned by the wrapped writer. It does not test behavior when the wrapped writer itself is unsafe under concurrent writes, which is documented as outside `CountWriter`'s responsibility.
