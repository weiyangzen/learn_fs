## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/network-tests/src/test/blockade/ozone/util.py

Purpose: shell and polling utilities for blockade tests.

Important APIs/types/functions: `wait_until(predicate, timeout, check_frequency)` polls until a predicate returns true or asserts on timeout. `run_docker_command(command, run_on)` wraps `docker exec <container> bash -c <command>`. `run_command(cmd)` executes a shell command, captures stdout/stderr, logs output, returns `(returncode, output)`, and prints a simple duration. `get_checksum(file_path, run_on)` computes `md5sum` inside a container and extracts the checksum.

Control flow: command list fragments are joined with spaces before execution. `run_command` uses `subprocess.Popen(shell=True)` and `communicate`, then normalizes output with a regex.

State and persistence behavior: no local persistence; effects are external shell, docker, filesystem, and Ozone operations.

Dependencies and integration points: depends on `Command.docker`, Python `subprocess`, `time`, and `re`. Used by `Blockade`, `OzoneClient`, `OzoneCluster`, and tests.

Risks: shell=True with interpolated values, no timeout for commands, regex output normalization can alter diagnostics, and `wait_until` depends on asserts. String/bytes behavior is Python-version sensitive.

Test signals: every docker/Ozone command in blockade tests flows through this module, so failures are visible as nonzero exit codes and captured output.
