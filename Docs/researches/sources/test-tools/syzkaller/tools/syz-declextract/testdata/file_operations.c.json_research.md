# sources/test-tools/syzkaller/tools/syz-declextract/testdata/file_operations.c.json

Purpose: this golden JSON captures expected extraction for the file-operations fixture.

Important structure: top-level keys are `functions`, `consts`, `structs`, `file_ops`, and `ioctls`. Functions include helper functions from `include/fs.h`, all `foo_*`, `proc_*`, and `unused_ioctl` callbacks. Constants include the reachable `FOO_IOCTL*` values and local `FOO_IOCTL12`. Structs include `foo_ioctl_arg` with size 8, alignment 4, and fields `a` and `b`.

Control-flow and integration: `foo_ioctl` contains a command scope for direct ioctls and facts mapping its `cmd` and `arg` parameters into `foo_ioctl2`. `foo_ioctl2` contributes scopes for `FOO_IOCTL6` and `FOO_IOCTL7`. File operation records associate operation tables with callbacks, while ioctl records encode command names, directions, and argument struct usage.

State and persistence: static test cache input; line numbers and enum/macro values must track the C fixture.

Risks and test signals: verifies that reachable file operations are retained, unused ioctl-only operations are not over-promoted into descriptions, and nested ioctl helper calls are represented. It is sensitive to JSON schema and source line churn.
