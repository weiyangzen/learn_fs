<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/rsyncstats -->
# sources/sync-backup/rsync/support/rsyncstats

Purpose: Perl report generator for rsync daemon transfer logs, producing daily, hourly, archive-section, and domain summaries.

Important APIs/types/functions: main parsing/report loop, Perl formats `top1/line1`, `top2/line2`, `top3/line3`, `top8/line8`, comparator subs `datecompare`, `domnamcompare`, `bytecompare`, `faccompare`, and `usage()`. Options include `--hourly-report`, `--domain-report`, `--total-report`, `--depth-limit`, `--domain`, `--section`, and `--file`.

Control flow: parse options, open the log file, optionally print filters, parse lines matching syslog-like or rsyncd-like prefixes and default transfer-log fields, normalize itemized `%i` operations to send/recv, build module/file path keys up to a depth limit, filter by section/domain, aggregate file and byte counts by date, hour, section, and domain, then render formatted reports for selected dimensions.

State and persistence behavior: read-only over the log file; all aggregation is in memory. It exits if no data matched.

Dependencies and integration points: depends on Perl, `Getopt::Long`, rsync daemon transfer log format, and default `/var/log/rsyncd.log` unless overridden.

Risks: regex parsing is tightly coupled to log format and IPv4 bracket field shape. Domain classification treats numeric-looking hosts or short names as `unresolved`. The code has legacy globals without `strict`, making typo bugs easier. Send/recv separation is noted as TODO and not reflected in separate totals.

Test signals: fixture logs should cover syslog and rsyncd prefixes, `%o` and `%i` operation styles, section/domain/depth filters, no-data errors, and each optional report format.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/rsyncstats -->
