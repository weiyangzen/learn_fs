# sources/storage-engines/wiredtiger/tools/antithesis/launch_gdb.sh

## Purpose
`launch_gdb.sh` is a developer helper for opening a WiredTiger `test/format` core file inside the Antithesis Docker image. It ensures the image exists, mounts the core at the expected location, and runs `gdb t core`.

## Important commands and variables
The script requires being run from `tools/antithesis`. It checks for a `wt-test-format` image with `sudo docker image ls | grep`, builds `wt-test-format:latest` from `test_format.dockerfile` if absent, resolves the first argument to an absolute source path, sets `T_DIR=/opt/bin/test/format`, and runs a temporary interactive container with `--mount type=bind,src=$SRC,dst=$T_DIR/core`.

## Control flow and behavior
The working-directory guard exits with a clear message if invoked from the wrong folder. If the image check fails, the script builds the image from the repository root. Then it launches an interactive container and changes to the test directory before invoking GDB on executable `t` and mounted core file `core`.

## State, dependencies, and integration
The script depends on Docker, sudo privileges, `test_format.dockerfile`, and a core path argument. It integrates with the same image used by Antithesis test runs, which helps match libraries and binaries during postmortem debugging.

## Risks and test signals
Risks include brittle image detection via grep, unquoted path handling, no explicit argument validation, and required interactive TTY/sudo access. Signals are an interactive GDB session with symbols and executable `t` resolved, or a locally built image when none existed.
