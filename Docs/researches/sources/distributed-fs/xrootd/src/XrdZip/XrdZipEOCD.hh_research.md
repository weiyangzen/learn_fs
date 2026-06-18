# sources/distributed-fs/xrootd/src/XrdZip/XrdZipEOCD.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdZip/XrdZipEOCD.hh` defines the End of Central Directory record representation for XRootD ZIP support. It locates, parses, constructs, serializes, and logs the EOCD metadata that terminates a ZIP archive and points to the central directory. The source was read as a complete 159-line file.

## Important APIs, Types, and Functions

`EOCD::Find()` scans backward for signature `0x06054b50`. The buffer constructor parses disk numbers, record counts, central-directory size and offset, comment length, optional bounded comment, computed `eocdSize`, and initializes `useZip64` false. The construction constructor takes central-directory offset, count, and size, writes overflow sentinels for 16-bit counts and 32-bit offsets as needed, and marks `useZip64` when the offset overflows. `Serialize()` writes the record to a `buffer_t`, and `ToString()` formats fields for logging. Constants include `eocdBaseSize = 22` and `maxCommentLength = 65535`.

## Control Flow

Finding an EOCD starts from `size - eocdBaseSize` and decrements to zero, returning the first matching signature. Parsing then reads fixed fields and, if `maxSize` is provided, validates that the comment fits before copying it. Serialization emits fixed fields followed by the comment. Archive-writing code uses the constructor to choose classic fields or overflow sentinels.

## State and Persistence Behavior

The struct is an in-memory form of persistent ZIP end metadata. Serialized state includes disk fields, central-directory counts, size, offset, and comment. `useZip64` is runtime guidance for writing ZIP64 structures and is not itself serialized in EOCD.

## Dependencies and Integration Points

The header includes `XrdZipUtils.hh`, `XrdZipLFH.hh`, `XrdZipCDFH.hh`, `<string>`, and `<sstream>`. It integrates with central-directory construction, ZIP64 overflow handling, archive scanning, and logging.

## Risks and Edge Cases

`Find()` takes an unsigned `size` and computes `size - eocdBaseSize` before assigning to `ssize_t`; if `size` is smaller than the base size, unsigned underflow can produce an invalid starting offset. The constructor marks ZIP64 only when the central-directory offset overflows, not when record count or size overflows; count overflow writes sentinels but does not set `useZip64` by itself in the visible code. `ToString()` omits an `=` after `cdSize`, a harmless logging defect. Bounded parsing depends on callers passing `maxSize`.

## Test Signals

Tests should cover finding EOCD with empty and maximum comments, no signature, buffers smaller than 22 bytes, false signatures inside comments, bounded parse truncation, record-count overflow, offset overflow, central-directory size overflow expectations, serialization round trip, and `ToString()` content for diagnostics.
