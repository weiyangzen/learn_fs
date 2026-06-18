<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/filter_process_scanner_test.go -->
# sources/sync-backup/git-lfs/git/filter_process_scanner_test.go

## Research

This file tests the filter-process scanner with in-memory pkt-line buffers. It verifies successful initialization writes server/version packets, invalid welcome messages and unsupported versions are rejected without output, supported capabilities are negotiated, unsupported capability sets fail, request headers and multi-packet payloads are read, invalid packet length is surfaced, and `WriteList` emits correct pkt-line framing.

The tests provide strong protocol regression coverage without invoking Git. Remaining gaps include delay capability acceptance, `WriteStatus`, EOF behavior, malformed header key/value pairs, reading multiple sequential requests, and payload-not-drained desynchronization.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/filter_process_scanner_test.go -->
