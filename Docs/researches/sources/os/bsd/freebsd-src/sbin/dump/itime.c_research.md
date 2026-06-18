# File Research: sources/os/bsd/freebsd-src/sbin/dump/itime.c

Maintains `/etc/dumpdates` state for `dump`, including reading prior dump records, selecting the base time for incremental dumps, and writing updated records.

Key responsibilities:
- `initdumptimes()` opens or creates the dumpdates file and takes a shared lock while reading.
- `readdumptimes()` parses all records into an SLIST, then builds `ddatev`, an array view used by iteration macros.
- `getdumptime()` finds the most recent dump of the same filesystem at a lower level and stores it in `spcl.c_ddate`.
- `putdumptime()` takes an exclusive lock, rereads current records, updates/adds this dump level, rewrites the file, truncates trailing old data, and reports the completed dump date.

Important data:
- `dumpdates`: path to dumpdates file, defaulted in `main.c`.
- `nddates`, `ddatev`, and `dthead`: in-memory dump date database.
- `lastlevel`: previous dump level selected for the current dump.
- `recno`: parser line counter, reset in `getrecord()`.

Parsing and formatting:
- Records use `DUMPINFMT` / `DUMPOUTFMT` from `<protocols/dumprestore.h>`.
- `makedumpdate()` parses the ctime-like date with `unctime()`.
- `dumprecout()` validates name length against `DUMPFMTLEN`.

Risks and constraints:
- `recno` resets for each `getrecord()` call, so malformed line reporting does not reflect absolute file line number.
- Update path allocates a fresh record for new entries but old SLIST storage is not globally freed; acceptable for a short-lived utility.
- Time fields convert between FreeBSD dump protocol time widths and `time_t` using `timeconv.h`.
