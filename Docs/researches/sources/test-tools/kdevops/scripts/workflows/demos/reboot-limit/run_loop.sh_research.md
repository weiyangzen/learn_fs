# sources/test-tools/kdevops/scripts/workflows/demos/reboot-limit/run_loop.sh

## Purpose
Runs the reboot-limit baseline Make target repeatedly until a configured steady-state loop goal is reached or a failure occurs.

## Important APIs
`run_loop()` is the main loop body. It uses common kernel-CI log variables from `scripts/lib.sh`, especially `.kernel-ci.ok`, `.kernel-ci.fail`, `.kernel-ci.log`, `.kernel-ci.fail.log`, `.kernel-ci.diff.log`, and `.kernel-ci.logtime.loop`.

## Control flow
It sources `.config` and `scripts/lib.sh`, resumes count from `.kernel-ci.ok` when incremental mode is enabled, runs `/usr/bin/time -p -o .kernel-ci.logtime.loop make reboot-limit-baseline`, records git status and timing, writes diff/failure files on nonzero return, appends each iteration to the full log, updates `.kernel-ci.ok`, and exits once `CONFIG_REBOOT_LIMIT_ENABLE_LOOP=y` and count exceeds `CONFIG_REBOOT_LIMIT_LOOP_STEADY_STATE_GOAL`.

## State and persistence
Persists kernel-CI style loop files in the current working directory. The invoked Make target may separately persist reboot-limit result files and reboot target systems repeatedly.

## Dependencies and integration
Depends on kdevops Make targets, `/usr/bin/time`, Git, Ansible/SSH access through the Make target, sourced Kconfig variables, and the reboot-limit workflow layout.

## Risks and test signals
This is intentionally disruptive because `make reboot-limit-baseline` reboots hosts. The script overwrites kernel-CI log files and records git diffs on failure. Test with a low steady-state goal and disposable host, and verify `.kernel-ci.ok` resume behavior.
