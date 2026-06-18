# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/explicit_dir/list_test.go

Purpose: verifies listing behavior when implicit directories are disabled. It ensures only explicit directory objects and files are visible, and statting an implicit directory after list returns not-exist.
Important APIs/functions: `TestListOnlyExplicitObjectsFromBucket` and `TestStatImplicitDirAfterList`.
Control flow: tests create a mixed implicit/explicit directory structure using either storage-client helpers for zonal runs or mounted/object helpers for other runs. `filepath.WalkDir` reads directories and checks expected names, ordering, directory flags, and counts.
State and persistence: backing GCS contains both implicit object prefixes and explicit directory marker/file objects. Mounted listing should filter out implicit-only directories in this package configuration.
Dependencies and integration points: depends on shared constants in `implicit_and_explicit_dir_setup`, `setup.SetupTestDirectory`, storage client in `testEnv`, and explicit-dir package setup flags.
Risks and edge cases: assertions rely on deterministic `os.ReadDir` lexical ordering. TODOs show zonal bucket setup path differs from non-zonal, which can hide behavior differences.
Test signals: root listing contains only explicit dir/file, explicit dir contains its files, and stat of implicit directory yields `os.ErrNotExist` after list.
