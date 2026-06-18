# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/tapfs.c

This file implements a tapefs backend for old `tap` tape images.

Key behavior:
- Reads a fixed directory table of old tap entries.
- Verifies each entry checksum.
- Extracts file address, size, mode, uid, timestamp, and name.
- Converts absolute names to relative names and inserts entries into the shared tree.
- Reads file data from 512-byte block addresses.

Important details:
- Supports old and “newtap” timestamp interpretation.
- Skips entries with empty names, zero addresses, or checksum failures.
- Does not support directories beyond path-derived parent creation unless entries imply them through names.

Filesystem relevance:
- Direct: exposes historical tap tape archive contents through 9P.
