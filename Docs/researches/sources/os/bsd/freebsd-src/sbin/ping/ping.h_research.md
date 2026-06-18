# File Research: sources/os/bsd/freebsd-src/sbin/ping/ping.h

## Purpose
Minimal IPv4 ping interface header.

## Main Elements
Declares `int ping(int argc, char *const *argv);`.

## Dependencies And Integration
Included by `main.c` when INET support is compiled.

## Risk Notes
Small ABI surface; signature must match `ping.c`.
