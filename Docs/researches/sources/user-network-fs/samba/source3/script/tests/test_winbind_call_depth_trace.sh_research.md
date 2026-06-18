# sources/user-network-fs/samba/source3/script/tests/test_winbind_call_depth_trace.sh

Purpose: verifies winbind debug trace call-depth logging and indentation for a nested group membership query.

Important functions and APIs: uses `smbcontrol`, `global_inject.conf`, `id`, `grep`, and subunit. `test_winbind_call_depth_trace()` injects `debug syslog format = no` and `log level = 10`, reloads winbind, runs `id ADDOMAIN/alice`, clears the injected config, reloads again, then checks log growth and formatting.

Control flow: the script first maps `TESTENV` to a log directory and skips if only stdout logging is available. It only permits `ad_member*` environments. The test records the count of `wb_group_members_send` lines before/after the `id` command, expects the count to increase, expects the last such trace to include `depth=3`, and expects the related `WB command group_members start` line to be indented by 14 spaces.

State and persistence: temporarily modifies `global_inject.conf` and appends to the winbind log through debug logging. It resets the file to empty after the command.

Dependencies and integration: registered as `samba3.winbind_call_depth_trace` for `ad_member:local`. It depends on log file path conventions and exact debug output formats.

Risks and test signals: log formatting and function-name changes will break the grep checks. If winbind logs to stdout via `WINBINDD_DONT_LOG_STDOUT=1`, the script skips rather than failing because debug headers are absent.
