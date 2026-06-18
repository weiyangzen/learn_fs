## sources/test-tools/syzkaller/pkg/image/fsck_test.go

Purpose: integration tests for `Fsck` using real filesystem images and host fsck tools.

Important APIs/types/functions: `TestFsck` and `corruptedFs` fixture bytes.

Control flow: test checks tool availability, then runs `Fsck` on known clean and corrupted inputs and asserts output/clean/error behavior.

State and persistence: creates temporary image files indirectly through `Fsck`.

Dependencies and integration: depends on external fsck binaries being installed; skips or adapts when unavailable.

Risks: host-environment sensitive; external fsck versions can change output details.

Test signals: verifies the subprocess/sandbox path rather than only parser logic.
