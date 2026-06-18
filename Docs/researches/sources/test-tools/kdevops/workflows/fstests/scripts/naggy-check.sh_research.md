## sources/test-tools/kdevops/workflows/fstests/scripts/naggy-check.sh

Purpose: Repeatedly runs fstests `./check` for one or more tests until a count is reached or, optionally, a failure occurs.

Important APIs/types/functions: Functions include `known_hosts_local`, `get_config_sections`, `parse_config_section_local`, `sig_exit`, and `parse_args`. CLI options include `--section`, `--count`, and `--fail-triggers-exit`.

Control flow: The script resolves host options, infers a section from the hostname, parses default and selected config sections, then loops over `./check -s $SECTION $TESTS`. It reports PASS/FAIL per iteration and per test by inspecting `.out.bad` and `.dmesg` result files.

State and persistence: It writes normal fstests result artifacts through `./check`; it does not manage cleanup. It reads config from `/var/lib/xfstests/configs` or local options.

Dependencies and integration points: Requires an fstests tree, `./check`, result layout under `results/$(hostname)/$(uname -r)/$SECTION`, and host config syntax compatible with xfstests/kdevops.

Risks and test signals: The loop can run indefinitely by default. Test with `--count 1` and a known passing/failing test, and verify per-test failure detection against generated result files.
