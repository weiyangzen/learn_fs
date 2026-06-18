<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/eventlogadm.c -->
# sources/user-network-fs/samba/source3/utils/eventlogadm.c

## Purpose
`eventlogadm.c` is a Samba command-line utility for managing Windows-style event logs backed by TDB and Samba registry data. It can write event records from stdin, dump stored records, and add event source registry entries.

## Important APIs, types, and functions
- `usage()` and `display_eventlog_names()` present command help and configured event logs.
- `eventlog_add_source()` validates an event log, updates its `Sources` `REG_MULTI_SZ`, creates the source subkey, and writes `EventMessageFile`.
- `DoAddSourceCommand()` initializes registry access, wraps `eventlog_add_source()` in a registry transaction, and commits/cancels.
- `DoWriteCommand()` opens an eventlog TDB, parses log-entry text from stdin with `parse_logentry()`, normalizes records with `fixup_eventlog_record_tdb()`, and stores them using `evlog_push_record_tdb()`.
- `DoDumpCommand()` reads records by number with `evlog_pull_record_tdb()` and prints them with NDR formatting.
- `main()` parses `-o`, `-s`, `-d`, and `-h`, loads configuration, and dispatches `write`, `addsource`, or `dump`.

## Control flow
Default operation is `write`. After getopt parsing and config load, `main()` dispatches by operation name. `write` reads stdin line by line until `parse_logentry()` marks end-of-record, then writes non-null timestamped records. `addsource` starts a registry transaction before updating source metadata. `dump` starts at record 1 or the supplied record number and prints records until no record is returned.

## State and persistence behavior
`write` persists event records into the named eventlog TDB. `addsource` persists registry changes under `KEY_EVENTLOG\<eventlog>`, including the `Sources` list and source subkey. `dump` is read-only. The configured eventlog list comes from smb.conf.

## Dependencies and integration points
The file depends on Samba eventlog APIs, registry APIs, admin token creation, registry DB backend transactions, NDR printing for eventlog records, loadparm, `fstring`, and string wrappers. It is an administrative bridge between textual event records, eventlog TDBs, and registry metadata.

## Risks and edge cases
- `write` uses a fixed 1024-byte input line buffer, so long fields may be truncated by `fgets`.
- `eventlog_add_source()` expects an existing valid eventlog registry key and an existing `Sources` value of type `REG_MULTI_SZ`.
- Failure while setting `EventMessageFile` returns directly rather than flowing through the final cleanup path, although the talloc frame is process-scoped.
- `dump` loops until a missing record, so sparse records stop output.

## Test signals
Useful tests create a configured eventlog, add a source, write sample stdin records, dump from record 1 and later offsets, and verify registry `Sources` and `EventMessageFile` values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/eventlogadm.c -->
