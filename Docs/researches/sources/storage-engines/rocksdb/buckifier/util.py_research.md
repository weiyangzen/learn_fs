# sources/storage-engines/rocksdb/buckifier/util.py research

Purpose: `util.py` provides small shared helpers for RocksDB buckifier scripts: terminal coloring and shell-command execution with optional verbose logging. It supports both Python 2 and Python 3 compatibility.

Important APIs: `ColorString` exposes ANSI color constants plus static methods `ok()`, `info()`, `header()`, `error()`, and `warning()`. The class-level flag `ColorString.is_disabled` disables coloring. `run_shell_command(shell_cmd, cmd_dir=None)` runs a single shell command and returns `(returncode, stdout, stderr)`. `run_shell_commands(shell_cmds, cmd_dir=None, verbose=False)` executes a sequence and returns a boolean success indicator.

Control flow: `run_shell_command()` optionally creates `cmd_dir`, starts `subprocess.Popen(shell=True)`, captures stdout/stderr, waits for completion, and reports elapsed time for commands running longer than five minutes. `run_shell_commands()` iterates commands, prints captured output only when verbose or failing, and stops at the first nonzero return code.

State and persistence: no persistent state is maintained except directories created for `cmd_dir`. The main mutable state is the global color-disable flag. Commands can mutate the filesystem depending on their shell text.

Dependencies and integration: it depends on `os`, `subprocess`, `sys`, and `time`. The helper is intended for other buckifier scripts that need simple command orchestration and colored status output.

Risks and test signals: `shell=True` plus string interpolation is command-injection prone if untrusted input reaches these helpers. Automatic `mkdir -p` is also built from a raw shell string. Captured output is bytes under Python 3, so downstream formatting can differ from text expectations. Tests should cover command success/failure, verbose output behavior, disabled colors, Python 2/3 byte/text behavior, and missing-directory creation.
