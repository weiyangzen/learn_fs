<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/example_test.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/example_test.go

Purpose: documentation-style example for using spawntest helpers with HTTP JSON control.

Important APIs, types, and functions: defines a registry, `addRequest`, `addResult`, `add`, `addHelper`, example test/main functions, and `Example`.

Control flow: the disabled-by-name test spawns a helper subprocess, sends JSON to `/`, and checks the addition result. The disabled `TestMain` shows flag and helper dispatch setup.

State and persistence behavior: no persistent state; helper process lifetime is controlled by `Control.Close`.

Dependencies and integration points: demonstrates `spawntest.Registry`, `Helper.Spawn`, and `httpjson.ServePOST`.

Risks and test signals: functions are prefixed `name_me_` to keep them illustrative rather than active; underscore assignments quiet linters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/example_test.go -->
