<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/filter_process_scanner.go -->
# sources/sync-backup/git-lfs/git/filter_process_scanner.go

## Research

`filter_process_scanner.go` implements Git filter-process pkt-line protocol scanning. `FilterProcessScanner` owns a `pktline.Pktline`, current `Request`, and last error. `Init` performs the `git-filter-client`/`git-filter-server` version=2 handshake. `NegotiateCapabilities` requires clean and smudge, accepts delay when Git offers it, and writes selected capabilities.

`Scan` reads one request header packet list and exposes a payload reader backed by pkt-line until flush. `Request` and `Err` report the last scan result. `WriteList` and `WriteStatus` write response lists/status values. State is sequential and not synchronized; callers must consume each payload before scanning the next request. Dependencies include `pktline`, custom errors, translations, slices, and tracer logging. Risks include protocol desynchronization if payloads are not fully read, unsupported capability handling, scanner lifecycle around EOF, and header parsing that ignores malformed pairs without `=`. Tests cover handshake, capability negotiation, request/payload reading, invalid packet errors, and list writing.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/filter_process_scanner.go -->
