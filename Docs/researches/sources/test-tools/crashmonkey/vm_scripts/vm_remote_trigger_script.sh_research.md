# sources/test-tools/crashmonkey/vm_scripts/vm_remote_trigger_script.sh

Purpose: remote VM script that prepares CrashMonkey, compiles copied workloads, and launches XFSMonkey for a requested filesystem.

Important APIs/types/functions: arg `fs`, process guards for `xfsMonkey` and `vm_remote_trigger_script`, `apt-get install`, `git checkout .`, `git pull`, `git checkout master`, log/diff cleanup, `cm_cleanup.sh`, `/mnt/snapshot`, workload copy from `~/seq2`, `make`, `build/xfsMonkeyTests`, and `nohup sudo python xfsMonkey.py`.

Control flow: validates filesystem arg, exits if a run/trigger appears active, installs packages, updates repo, removes logs/diffs, performs module/mount cleanup, recreates mount point, removes old j-lang sources and shared objects, copies new workloads, compiles, moves built `.so` files into `build/xfsMonkeyTests`, then starts XFSMonkey in the background with output log.

State/persistence behavior: heavily mutates the remote CrashMonkey checkout, installed packages, build outputs, logs, diff results, kernel module/mount state, and starts a long-running root test process. Dependencies/integration: central remote execution path for distributed workloads.

Risks/test signals: destructive `git checkout .` discards remote changes, hard-coded password/path/device, weak process guards, no `set -e`, and background command composition with `nohup echo password | sudo -S python ... &` is fragile.
