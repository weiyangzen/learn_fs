## sources/user-network-fs/gcsfuse/internal/util/util_test.go

Purpose: Tests path resolution and MiB/byte conversion utilities.

Important APIs/types/functions: Ogle-style `UtilTest` suite covers `GetResolvedPath`, `MiBsToBytes`, and `BytesToHigherMiBs`.

Control flow: path tests exercise absolute, empty, tilde, dot, dotdot, and plain relative paths with and without `GCSFUSE_PARENT_PROCESS_DIR`. Conversion tests cover zero, normal values, maximum supported MiB, and overflow-to-next-MiB behavior.

State and persistence behavior: temporarily sets/unsets `GCSFUSE_PARENT_PROCESS_DIR` and reads current working/home directories.

Dependencies and integration points: validates child-process path behavior described in `util.go`.

Risks: several suite methods are named without the `Test` prefix (`ResolveEmptyFilePath`, `ResolveWhen...`) and may not run under the suite framework depending on its discovery rules. The panic path for `MiBsToBytes` is not covered.

Test signals: useful coverage for common path and conversion cases, with a possible test-discovery gap for non-prefixed methods.
