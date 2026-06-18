# File Research: sources/virtualization/nbd/nbd-trdump.c

## Purpose
Implements `nbd-trdump`, a command-line utility that reads an NBD transaction log from standard input and prints a human-readable stream of requests, replies, structured replies, and trace-log option records.

## Main Entry Points
- `doread()` reads an exact byte count from a file descriptor, exiting cleanly on EOF or with an error on read failure.
- `main()` validates optional help usage, then loops over log records by magic value and decodes each record.

## Control Flow
The utility reads a 32-bit magic number, converts it from network order, and dispatches on the record type. Request records decode cookie, command, offset, and length, then print command text from `getcommandname()`. Reply records print cookie and error. Trace-log records update `g_with_datalog` when `NBD_TRACELOG_SET_DATALOG` is seen. When datalog is active, write payload bytes after a write request are consumed and discarded. Structured replies print cookie, type, flags, and payload length.

## Dependencies
Uses `cliserv.h`, `nbd.h`, and `nbd-helper.h` for protocol constants, byte-order helpers, and command-name formatting.

## Risks and Notes
Structured reply `paylen` is a 32-bit field, but the code converts it with `ntohs()` instead of `ntohl()`, so displayed payload lengths can be wrong for larger values. The tool intentionally does not interpret structured reply payload bodies.
