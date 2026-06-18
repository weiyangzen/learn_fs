# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclio.h

Command-list I/O abstraction header. It defines `clist_file_ptr` as an opaque pointer and documents the two interchangeable implementations: external filesystem storage and embedded RAM-backed storage, selected at compile/link time.

The API covers opening/creating scratch files, closing with optional deletion, unlinking, space-availability queries, byte writes, byte reads, low-memory warning thresholds, error-code status, current position, rewind with optional data discard, and seek. The interface deliberately passes file names to rewind/seek so implementations that must close/reopen backing storage can do so.
