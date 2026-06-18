# File Research: sources/os/bsd/openbsd-src/sbin/dump/itime.c

## Purpose
Reads, interprets, updates, and writes `/etc/dumpdates`.

## Key Behavior
- `initdumptimes()` opens the dumpdates file, creates it if missing, takes a shared lock, and reads records.
- `readdumptimes()` builds a linked list and an array view of dumpdate records.
- `getdumptime()` selects the most recent lower-level dump record for the current disk/DUID and stores it in `spcl.c_ddate`.
- `putdumptime()` takes an exclusive lock, rereads the file, updates or appends the current dump level/date, rewrites records, flushes, and truncates the file.
- `makedumpdate()` parses records using `DUMPINFMT`, canonicalizes names through DUID lookup when possible, and parses ctime-style timestamps with `strptime()`.

## Notes
The code supports both device names and DUIDs so historical dump records can match modern disk identifiers.
