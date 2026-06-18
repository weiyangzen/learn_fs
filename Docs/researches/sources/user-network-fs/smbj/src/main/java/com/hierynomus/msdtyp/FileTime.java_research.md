# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdtyp/FileTime.java

Source read signal: reviewed complete local file (93 lines, 2801 bytes).

## Purpose
`FileTime.java` covers Windows FILETIME value object. converts between Windows 100ns timestamps, Unix epoch milliseconds, `Instant`, and `Date`.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Factory methods convert input units to Windows epoch offset; getters convert back with `TimeUnit`; equality/hash are timestamp-based.

## State and persistence
Immutable `windowsTimeStamp` field.

## Dependencies and integration points
Used by SMB file information classes and MS-DTYP helpers.

## Risks
Precision loss occurs when converting through milliseconds; overflow is possible for extreme dates.

## Test signals
Signals are timestamp conversion unit tests around epoch, now, and roundtrips.
