# sources/user-network-fs/rclone/backend/union/union_test.go

Purpose: external union backend configurations for the generic rclone filesystem test suite.

Important APIs: `TestIntegration`, `TestStandard`, `TestRO`, `TestNC`, `TestPolicy1`, `TestPolicy2`, `TestPolicy3`, and unimplementable method lists.

Control flow/state: synthetic tests create temp local upstreams and configure policies/suffixes through `fstests.ExtraConfigItem`: standard `epall/epmfs/ff`, read-only suffixes, no-create suffixes, `all/lus/all`, `all/rand/ff`, and `all/all/all`.

Dependencies/integration: imports local and memory backends for registration, plus union, `fstest`, and `fstests`.

Risks/test signals: broad contract coverage for common configs, but not exact placement assertions. `QuickTestOK` keeps local runs fast.
