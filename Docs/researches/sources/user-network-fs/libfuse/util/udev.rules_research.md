# sources/user-network-fs/libfuse/util/udev.rules

## Purpose
udev rule granting broad access to the FUSE kernel device node.

## Important APIs, Types, And Functions
- Single rule: `KERNEL=="fuse", MODE="0666"`.

## Control Flow
udev applies the rule when creating or updating the device node named `fuse`.

## State And Persistence
Installed as a persistent udev rules file, typically `99-fuse3.rules`, affecting `/dev/fuse` permissions.

## Dependencies And Integration Points
Installed by `install_helper.sh` when a udev rules directory is known. Enables non-root FUSE helpers and libraries to open `/dev/fuse` subject to other policy checks.

## Risks
World-writable `/dev/fuse` is expected for FUSE but broad; system policy may prefer group ownership or ACLs. Packaging must ensure rule ordering does not conflict with distribution defaults.

## Test Signals
Reload udev rules, recreate `/dev/fuse`, verify mode, and test non-root open of `/dev/fuse`.
