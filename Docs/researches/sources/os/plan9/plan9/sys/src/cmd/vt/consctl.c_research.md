# File Research: sources/os/plan9/plan9/sys/src/cmd/vt/consctl.c

This file simulates Plan 9 console control files for the terminal emulator.

Core behavior:
- `consctl` attaches a small shared segment named `shared` to hold a `Consstate`.
- Binds pipes over `/dev/consctl` and `/dev/cons` using `/mnt/cons/consctl` and `/mnt/cons/cons`.
- Forks a child that watches `/mnt/cons/consctl/data` for control messages.

Recognized control tokens:
- `rawon` / `rawoff` toggle `x->raw`.
- `holdon` / `holdoff` toggle `x->hold`.

Lifecycle:
- Parent returns the shared `Consstate*`.
- Child loops up to 100 failed/open cycles, resetting state when reopening the control pipe.
- `notify(0)` disables note handling in the watcher child.

Role:
- Allows the shell or hosted program running under the terminal to control raw/cooked behavior through Plan 9-style `/dev/consctl`.
