# sources/user-network-fs/samba/source4/torture/smb2/notify_disabled.c

## Purpose

`notify_disabled.c` is a small Samba torture suite that verifies the server behavior when SMB2 change notify support is disabled or unavailable. Instead of expecting a pending async request and later filesystem-triggered completion, it opens a directory, submits one `CHANGE_NOTIFY` request, and requires `NT_STATUS_NOT_IMPLEMENTED`.

The exported entry point `torture_smb2_notify_disabled_init()` creates the `change_notify_disabled` suite and registers a single one-tree SMB2 test named `notfiy_disabled` (the spelling appears in the source).

## Important APIs, Types, and Functions

- `torture_smb2_notify_disabled()` is the sole test body. It uses `struct torture_context`, `struct smb2_tree`, `union smb_open`, `union smb_notify`, `struct smb2_handle`, and `struct smb2_request`.
- SMB2 calls are limited to directory setup and notify probing: `smb2_deltree()`, `smb2_util_rmdir()`, `smb2_create()`, `smb2_notify_send()`, `smb2_notify_recv()`, and `smb2_util_close()`.
- Assertions use `torture_assert_ntstatus_equal_goto()` instead of the custom macros used in `notify.c`.
- The test creates a temporary directory under `test_notify_disabled`, using `SEC_FILE_ALL`, directory create options, normal attributes, and read/write sharing.

## Control Flow

The test removes any stale `test_notify_disabled` directory, creates the directory with `NTCREATEX_DISP_CREATE`, and stores the returned directory handle. It then initializes an SMB2 notify request with a 1000-byte buffer, `FILE_NOTIFY_CHANGE_NAME`, the directory handle, and recursive mode enabled.

Unlike the normal notify suite, it does not create or remove a child object to trigger completion. It immediately calls `smb2_notify_recv()` after `smb2_notify_send()` and asserts that the server returns `NT_STATUS_NOT_IMPLEMENTED`. If that status is observed, it closes the directory handle, asserts close success, and deletes the temporary directory in the shared cleanup block.

## State and Persistence Behavior

The file has no persistent local state. The only server-side state is the temporary directory and its open handle. Cleanup always calls `smb2_deltree()` on `test_notify_disabled`, and the handle is closed on the success path before cleanup. If creation fails before a valid handle exists, the cleanup path still removes the directory tree.

Because the expected notify result is immediate `NT_STATUS_NOT_IMPLEMENTED`, this test does not rely on event-loop progress, backend buffering, second tree connections, or asynchronous cancellation.

## Dependencies and Integration Points

The file includes the same broad Samba SMB2 torture and security headers as the full notify test, but its practical dependencies are the SMB2 client call layer and the torture registration API. The suite integrates through `torture_suite_create()` and `torture_suite_add_1smb2_test()`, making it selectable as `change_notify_disabled`.

This suite complements `notify.c`: `notify.c` validates enabled notify semantics, while this file validates the expected status when the feature is intentionally disabled.

## Risks and Edge Cases

- The registered test name is spelled `notfiy_disabled`; callers and dashboards may need to use that exact typo unless the source is changed.
- The code assumes disabled notify returns `NT_STATUS_NOT_IMPLEMENTED` synchronously enough for direct receive. A backend that leaves the request pending, returns `NT_STATUS_INVALID_DEVICE_REQUEST`, or reports another feature-disabled status would fail.
- On the path where `smb2_notify_recv()` fails with an unexpected status, the handle is not explicitly closed before `smb2_deltree()`. The tree cleanup may still remove server objects, but the test does not validate close behavior in failure cleanup.
- The broad include list mirrors the main notify suite and is larger than this file needs; this is harmless but increases compile coupling.

## Test Signals

Passing this test is a clear signal that a disabled change-notify configuration rejects SMB2 notify requests with the expected protocol status. Failing it means either the feature is unexpectedly enabled, the disabled path returns a different status, or the server mishandles the simple directory setup needed before the notify probe.
