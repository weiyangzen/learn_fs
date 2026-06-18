# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/parser/parser_test.go

Purpose: table-driven tests for LTM command parsing.

Important flow: defines expected ext4 config expansions and command cases such as `ltm smoke`, explicit `-c ext4/4k -g quick`, default configs, primary filesystem override, invalid options, and duplicate handling. `TestParse` compares valid args and config maps from `Cmd`.

State and dependencies: relies on local `/root/fs/...` config files being available, so some cases are appliance/environment dependent.

Integration points: protects command sanitization used before sharding test runs.

Risks and test signals: tests are only as deterministic as the config files they read. They do not cover quoting, missing `-c` argument panic, or base64 `DecodeCmd`.
