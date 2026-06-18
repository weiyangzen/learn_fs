<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/logfilter -->
# sources/sync-backup/rsync/support/logfilter

Purpose: Perl filter that extracts rsync daemon log lines belonging to a selected module or module subpath.

Important APIs/types/functions: main loop only. It defines regex prefixes for syslog and rsync log-file formats and tracks matching pids in `%pids`.

Control flow: take a module/path regex argument, parse each input log line for pid and message, detect session-start messages of the form `rsync on|to MODULE from`, mark or unmark that pid depending on whether the module matches, and print subsequent lines for marked pids.

State and persistence behavior: no file mutation; in-memory pid tracking persists across input lines so related transfer messages are emitted after the initial module match.

Dependencies and integration points: depends on Perl and rsync daemon log formats. It can read stdin or named log files.

Risks: the module argument is used as a regular expression, which is powerful but can surprise users expecting a literal name. Pid reuse inside a single log stream could misattribute lines if start/stop patterns are missing. Format changes may break parsing.

Test signals: sample syslog and rsyncd-format logs should cover matching modules, subdirectory matches, nonmatching modules, pid state reset, and regex metacharacters in module names.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/logfilter -->
