# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/parser/parser.go

Purpose: parses base64 user command lines and converts gce-xfstests config selection into LTM shardable filesystem/config lists while removing LTM-incompatible options.

Important APIs/state: `Cmd`, `sanitizeCmd`, `expandAliases`, `processConfigs`, `defaultConfigs`, `singleConfig`, and `DecodeCmd`. Constants set primary filesystem `ext4` and config root `/root`. Invalid boolean and option lists strip arguments such as `ltm`, instance/bucket/email/kernel/repo/bisect options, and monitor-timeout.

Control flow: `Cmd` splits on shell whitespace, strips invalid options and their values, expands `smoke` to `-c 4k -g quick`, and processes the first `-c` config argument. Config parsing supports `<fs>/<cfg>`, `<fs>`, `<cfg>`, and `<primary>:<fs>/<cfg>`, reading `.list` files under `/root/fs/<fs>/cfg/`.

State and dependencies: reads xfstests config files on disk; returns sanitized args and map of filesystem to config names.

Integration points: LTM `ShardScheduler` turns parsed configs into `fs/cfg` shard strings and passes sanitized args to each `gce-xfstests` shard command.

Risks and test signals: `strings.Fields` does not preserve shell quoting. `processConfigs` assumes `-c` has a following value and only handles the first one. Missing config files are silently ignored in `singleConfig`. Tests cover common config forms and invalid option stripping.
