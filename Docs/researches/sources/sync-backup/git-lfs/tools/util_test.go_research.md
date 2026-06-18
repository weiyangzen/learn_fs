# sources/sync-backup/git-lfs/tools/util_test.go

Purpose: common tests for copy callback and cross-platform clone helper availability.

Important APIs/types/functions: `TestCopyWithCallback` and `TestMethodExists`.

Control flow: copies a short buffer to discard with a callback and asserts one progress event; calls clone-support functions to ensure platform APIs are present.

State and persistence: no durable state; `CheckCloneFileSupported` may create temp files depending on platform.

Dependencies and integration points: validates `CopyWithCallback` behavior used by transfer adapters.

Risks: callback-count expectation depends on current buffer/copy behavior and clone optimization not firing for a bytes buffer.

Test signals: lightweight smoke coverage for core copy path.
