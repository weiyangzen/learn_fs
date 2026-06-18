# sources/storage-engines/rocksdb/tools/write_stress_runner.py

## Purpose

Python harness that repeatedly runs `./write_stress` for randomized intervals and modes, sometimes killing it violently, to exercise recovery and file cleanup across restarts.

## Important APIs, Control Flow, And Dependencies

`generate_runtimes` decomposes the requested total runtime into random short durations plus occasional 100/1000 second choices, capped by remaining time. `main` builds a shell command for each duration, randomly chooses kill mode versus clean shutdown, carries the DB across all but the first run with `--destroy_db=false`, and randomly toggles `--delete_obsolete_files_with_fullscan=true` and `--low_open_files_mode=true`. It uses `subprocess.Popen([cmd], shell=True)`, polls once per second, exits on unexpected nonzero child exit, kills in kill mode, then sleeps three seconds before the next run.

## State, Persistence, Integration, Risks, And Test Signals

The runner's state is the runtime schedule, first-run flag, child process, optional DB path, and Python RNG seeded from current time. It depends on a `write_stress` binary in the current directory. Risks include shell-string command construction, nondeterminism, no timeout guard around clean runs beyond the child runtime flag, and no explicit wait after `child.kill()`. The main signal is runner exit code: nonzero child exits are treated as failure, while killed processes in kill mode are expected and not considered errors.
