# File Research: sources/os/bsd/freebsd-src/sbin/devd/tests/client_test.c

## Purpose
Tests that `devd` client sockets deliver complete device events.

## Main Elements
- `create_two_events()`: creates and destroys a small `md(4)` null device to trigger DEVFS create/destroy events.
- `common_setup()`: connects to a `devd` Unix socket and triggers events.
- `seqpacket` test: reads from `/var/run/devd.seqpacket.pipe` and expects create/destroy events on separate packet reads.
- `stream` test: reads from `/var/run/devd.pipe` into a large buffer and searches for both event substrings.
- ATF registration adds both tests.

## Dependencies And Integration
Requires root because it uses `mdconfig`. Validates both SOCK_SEQPACKET and SOCK_STREAM client protocols implemented by `devd.cc`.

## Risk Notes
Tests may observe unrelated system events, so they search until target patterns are found or timeout/buffer limit is reached.
