# sources/sync-backup/bup/dev/prep-for-macos-build

## Purpose
Installs macOS build/test dependencies for bup CI using Homebrew and pip.

## Important APIs, Types, and Functions
Installs Homebrew if absent, then installs make, bash, par2, readline, rsync, pkg-config, md5sha1sum, Python, and pytest packages. Forces Homebrew readline link.

## Control Flow
Checks for `brew`, bootstraps it via official install script if needed, runs brew installs, force-links readline, then installs pytest/xdist with pip `--break-system-packages --user`.

## State and Persistence Behavior
Mutates Homebrew/pip state and readline symlink state.

## Dependencies and Integration Points
Used by Cirrus macOS task before configure/build.

## Risks and Test Signals
Risks are network/Homebrew drift, forced readline interference, and pip policy changes. Signal is successful dependency installation.
