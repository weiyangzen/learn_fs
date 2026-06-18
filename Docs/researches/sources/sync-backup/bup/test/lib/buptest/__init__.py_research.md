# sources/sync-backup/bup/test/lib/buptest/__init__.py

Purpose: Python subprocess helper module for bup tests, providing logged command execution with consistent result objects and optional stdout capture.

Important APIs/types/functions: `logcmd`, `exc`, `exo`, `ex_res = namedtuple('SubprocResult', ('out', 'err', 'rc'))`, `subprocess.run`, `PIPE`, and `bup.io.enc_shs`.

Control flow: `logcmd()` renders bytes or str command components through shell-safe quoting and prints the command to stderr. `exc()` logs, defaults `check=True`, runs the command, mirrors captured stderr to the real stderr if present, and returns `ex_res`. `exo()` ensures `stdout=PIPE`, logs, and delegates to `exc()`.

State and persistence behavior: executes real subprocesses, writes command traces and captured stderr to stderr, and returns captured output/return-code state. No module-level mutable state is maintained.

Dependencies/integration points: used across integration tests to run bup and Git commands while keeping readable logs. It depends on byte-safe shell rendering from `bup.io`.

Risks and test signals: default `check=True` means failing subprocesses raise before returning a result unless tests pass `check=False`. `logcmd()` currently only enters its print path when `cmd` is a string, while most callers pass byte sequences; command argument type handling is part of the helper contract.
