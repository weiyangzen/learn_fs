# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/netlib_history.c

Magic helper that renders historical versions of a Netlib file under `/usr/web/historic`. Query fields select `file` and optional `diff`; it rejects parent-directory traversal and overly long names.

It searches backwards by day for prior snapshots, lists up to 50 versions, or 10 with diffs. Diff mode gunzips `.gz` snapshots into temporary files and runs `diff -nb` between adjacent versions, embedding results in HTML.
