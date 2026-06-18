# sources/user-network-fs/samba/source3/script/scancvslog.pl

Purpose: legacy Perl script for extracting CVS log entries after a given date and matching a branch tag.

Important APIs, types, and functions: requires `timelocal.pl`, maps month names to numbers, and defines `make_time`, `get_tag`, and `get_entry`.

Control flow: parse logfile, optional start time, and optional tag; repeatedly collect entries separated by long asterisk lines; normalize the entry date; convert to epoch; compare date and tag; print matching entries.

State and persistence: reads a CVS log and writes matching entries to stdout.

Dependencies and integration: depends on old Perl `timelocal.pl` and historical CVS log formatting.

Risks: uses `@ARGV[n]` scalar oddities, rejects missing tag unless it equals empty extraction result, and has fragile date normalization. The special `19100` year workaround is legacy and suspicious.

Test signals: entries with full and abbreviated month names, missing dates, tag filters, empty start time, and separator edge cases.
