<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/syzbot/run-syz-command.sh -->
# sources/test-tools/syzkaller/tools/docker/syzbot/run-syz-command.sh

## Purpose

Runs a command inside a fresh shallow clone of syzkaller master.

## Important APIs, Types, and Functions

`mktemp -d`, `git clone --depth 1 --branch master`, `"$@"`, `rm -rf` cleanup after success.

## Control Flow

Creates temp dir, clones master, cd's into it, executes provided command, returns, removes clone.

## State and Persistence Behavior

No intended persistence on success; failures leave temp clone because no trap is installed.

## Dependencies and Integration Points

Requires Git/GitHub access; used inside syzbot container.

## Risks and Edge Cases

Always targets master; failed commands leak temp dirs.

## Test Signals

Run successful and failing commands to verify clone, cwd, and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/syzbot/run-syz-command.sh -->
