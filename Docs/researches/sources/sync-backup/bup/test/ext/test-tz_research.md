<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-tz -->
# sources/sync-backup/bup/test/ext/test-tz

Purpose: verifies bup save naming and commit author timezone formatting for half-hour time zones. Important APIs are `TZ`, `bup save -d`, Git `cat-file commit`, and `bup ls`. Control flow sets `TZ=Australia/Adelaide`, saves an empty `src` directory with a fixed Unix timestamp, checks the Git commit author timestamp contains the expected `+1030` offset, and verifies `bup ls /src` uses the correct local save name. State is the saved branch and environment timezone. Dependencies are system timezone data and Git commit formatting. Risks are missing zoneinfo data or timezone conversion changes. Test signals are exact author timestamp suffix and save listing.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test-tz -->
