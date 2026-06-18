# sources/test-tools/syzkaller/syz-ci/testdata/example.cfg

Purpose: sample syz-ci JSON configuration used by tests.

Important APIs/types/functions: contains global CI fields and two manager entries: `upstream-kasan` and `linux-next-kasan`.

Control flow: loaded by `TestLoadConfig` to exercise defaults, manager config parsing, dashboard/hub fields, and manager target configs.

State and persistence: fixture only.

Dependencies and integration points: paths and URLs model expected config schema for `loadConfig`.

Risks: sample uses placeholder addresses and absolute syzkaller paths; not intended for direct production deployment.

Test signals: guards against config schema regressions.
