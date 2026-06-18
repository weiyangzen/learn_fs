# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/delete_dir_test.go

Purpose: Tests recursive deletion of empty and non-empty explicit directories through `os.RemoveAll`.

Important APIs/types/functions: `TestDeleteEmptyExplicitDir` and `TestDeleteNonEmptyExplicitDir` use `setup.SetupTestDirectory`, `operations.CreateDirectoryWithNFiles`, `os.RemoveAll`, and `os.Stat`.

Control flow: each test creates a target directory under `dirForOperationsTest`; the non-empty case also creates files and a populated subdirectory. After `RemoveAll`, each test stats the removed path and fails if it still exists as a directory.

State/persistence: The non-empty case validates that deleting a directory removes descendant file objects and subdirectory markers from the bucket-backed namespace. No explicit per-test cleanup is needed beyond `RemoveAll`.

Dependencies/integration: Depends on shared operation constants and helper creation utilities.

Risks/test signals: The final stat check does not assert that the returned error is specifically not-exist, only that a valid directory no longer remains. Passing signals recursive directory deletion across explicit directory marker and object descendants.
