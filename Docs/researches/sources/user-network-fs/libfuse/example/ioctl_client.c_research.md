# sources/user-network-fs/libfuse/example/ioctl_client.c

## Purpose

`ioctl_client.c` is the minimal test client for the high-level `ioctl.c` filesystem. It opens the `fioc` file and either reads its current size or sets a new size using restricted ioctls. The source was read as a complete 74-line file.

## Important APIs, Types, and Functions

The single `main` function parses arguments, opens the target file, calls `ioctl(fd, FIOC_GET_SIZE, &size)` or `ioctl(fd, FIOC_SET_SIZE, &size)`, prints results, and closes the file.

## Control Flow

With one file argument it gets size and prints it. With a second argument it parses that argument with `strtoul` and sets size. Errors print via `perror` and return nonzero.

## State and Persistence Behavior

The client has no persistent state. Effects are changes to the mounted example filesystem's in-memory buffer.

## Dependencies and Integration Points

It depends on POSIX open/close/ioctl and `ioctl.h`. It targets the high-level `ioctl.c` example but also exercises compatible restricted ioctls in other examples.

## Risks and Edge Cases

`strtoul` errors and trailing characters are not checked, so invalid sizes can silently parse as zero or partial values. The client does not support unrestricted read/write ioctls.

## Test Signals

Run against a mounted `ioctl` filesystem for get, set, invalid path, invalid size text, permission failures, and repeated size changes.
