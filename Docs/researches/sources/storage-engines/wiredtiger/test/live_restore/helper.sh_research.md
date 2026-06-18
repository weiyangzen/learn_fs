# sources/storage-engines/wiredtiger/test/live_restore/helper.sh

Purpose: shared shell helper for live restore test scripts.

Important API: `live_restore_binary_path` points to `./test/cppsuite/test_live_restore`. `run_test` executes that binary with one argument string, captures the exit status, and accepts success or exit code 137. Other nonzero codes print diagnostic command/exit information and exit with the same code.

Control flow and state: the helper does not parse arguments itself and does not modify persistent files. It assumes callers source it from the build directory and pass a complete option string as `$1`.

Dependencies and integration: sourced by `short_test.sh` and `long_test.sh`. It depends on bash function syntax and the C++ suite `test_live_restore` binary being built at the expected relative path.

Risks and test signals: exit 137 is accepted because live restore tests may intentionally kill themselves. This can mask accidental SIGKILL/OOM failures if they also surface as 137, so surrounding logs are important. The unquoted `$live_restore_binary_path $1` intentionally allows option-string splitting but would not handle paths or values containing spaces.
