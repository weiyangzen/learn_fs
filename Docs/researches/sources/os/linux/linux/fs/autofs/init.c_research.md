# File Research: sources/os/linux/linux/fs/autofs/init.c

## Summary
Registers and unregisters the autofs filesystem and its misc-device ioctl interface.

## Main Responsibilities
- Define `autofs_fs_type`.
- Initialize `/dev/autofs` control device.
- Register the `autofs` filesystem.
- Unregister filesystem and misc device at module exit.

## Key APIs
- `init_autofs_fs()`.
- `exit_autofs_fs()`.
- `autofs_fs_type`.

## Important Behavior
The init path registers the misc device first, then the filesystem. If filesystem registration fails, the misc device is deregistered. Module aliases expose both filesystem and device names.

## Risks
Initialization ordering matters because the device ioctl path references `autofs_fs_type` and mount state. No complex runtime logic lives here.
