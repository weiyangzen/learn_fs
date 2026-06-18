# sources/test-tools/crashmonkey/xfsMonkey.py

Purpose: Python 3 runner that executes a directory of compiled CrashMonkey test shared objects through `build/c_harness`, collects diff files, and produces console/log summaries. It is the main local runner used by demo and remote VM scripts.

Important APIs/types/functions: `Log` stdout tee class, `build_parser`, `cleanup`, time helpers, `print_setup`, `ensure_sudo`, `validate_setup`, and `main`. CLI arguments include filesystem type, disk size, iterations, test device, flag device, and test path.

Control flow: `main` opens a timestamped log, tees stdout, parses/validates args, prints setup, creates `diff_results` and counter files, loops over `.so` files in the test path, builds a `c_harness` command for each, calls cleanup before each run, retries harness execution up to four times on failure, trims harness output around `Reordering`, writes log summaries, copies the last diff file through `copy_diff.sh`, then restores stdout and closes the log.

State/persistence behavior: requires root, unmounts `/mnt/snapshot`, unloads modules, creates `diff_results`, writes counters and `out`, runs kernel-module-backed harnesses, and writes timestamped logs. Dependencies/integration: depends on `build/c_harness`, `copy_diff.sh`, CrashMonkey kernel modules, test `.so` files, and Linux devices `/dev/sda`/`/dev/cow_ram0` by default.

Risks/test signals: shell=True command construction and relative paths are fragile, retries hide some harness errors, `iterations` argument is parsed but not used in the command, diff selection uses `tail -n -1` rather than a clear last-file expression, and cleanup errors are ignored.
