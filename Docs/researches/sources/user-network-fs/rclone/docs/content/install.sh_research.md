<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/content/install.sh -->
# sources/user-network-fs/rclone/docs/content/install.sh

## Purpose

`install.sh` is the public curl-piped installer for rclone release or beta binaries.

## Important APIs, Types, and Functions

It accepts an optional `beta` argument, detects unzip tools (`unzip`, `7z`, `busybox`), compares installed and current versions, detects OS/architecture, downloads the matching zip, extracts it, installs binary and man page, and exits with documented status codes.

## Control Flow

The script creates a temp directory, chooses an unzip tool, sets `XDG_CONFIG_HOME` to avoid root-owned user config, fetches release metadata, exits if current, maps `uname` OS/arch to rclone download names, downloads and extracts, installs into platform-specific locations, refreshes man databases where available, removes the temp directory, and prints a success message.

## State and Persistence Behavior

It mutates system paths such as `/usr/bin/rclone`, `/usr/local/bin/rclone`, and man directories. Temporary files are removed only on the normal path; early errors may leave temp dirs because no trap is installed.

## Dependencies and Integration Points

It depends on Bash, curl, one unzip implementation, uname, root permissions, optional mandb/makewhatis, and rclone download endpoints.

## Risks and Test Signals

Risks include curl-pipe trust, partial installs, missing cleanup trap, unsupported OS/arch mappings, beta/release endpoint failures, and permission differences. Tests should shellcheck, run in Linux/macOS/BSD containers where possible, mock download endpoints, and verify exit codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/content/install.sh -->
