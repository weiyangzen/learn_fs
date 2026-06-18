# sources/test-tools/syzkaller/pkg/cover/backend/modules_test.go

Purpose: provides a manual diagnostic test for Linux module discovery.

Important APIs/types/functions: package flag `-module_dir` and `TestLocateModules`.

Control flow: if no module directory is provided, the test skips. Otherwise it calls `locateModules` on the supplied directory and logs name-to-path mappings.

State and persistence: read-only traversal of the user-supplied module directory; no writes.

Dependencies and integration: uses Go `flag` and same-package `locateModules`. It is intended for developer validation against a real Linux build tree.

Risks: not an automated regression test, so module discovery behavior is mostly unguarded in CI. It logs output but has no assertions on expected modules.

Test signals: useful for ad hoc debugging of `.ko` discovery and module-name extraction; weak automated coverage.
