# sources/user-network-fs/samba/source3/utils/smb_prometheus_endpoint.c

`smb_prometheus_endpoint.c` is a libevent HTTP exporter for Samba smbd profile TDB metrics. It serves `/metrics`, collects aggregate worker/profile stats, optionally collects per-share stats, and writes Prometheus text exposition.

`struct export_state` holds the response buffer and HELP/TYPE one-shot flags. Export helpers handle authentication counters, CPU time counters, SMB1 request counters, SMB2 in/out byte counters, SMB2 latency histogram buckets/sum/count, and SMB2 failure counters. `export_profile_stats` repeatedly expands `SMBPROFILE_STATS_ALL_SECTIONS` with different macro definitions to visit the relevant stat families. `metrics_handler` performs the scrape; `default_handler` returns 404; `main` binds address/port and dispatches the event loop.

State is scrape-local except for the external profile TDB. The handler opens the TDB read/write with mutex locking for aggregate collection, then reopens read-only for per-service export. Dependencies are TDB, libevent2, and Samba `smbprofile` helpers.

Risks include unescaped metric label values from share names, a missing TDB close on `smbprofile_magic` failure, misleading HELP text for output bytes, and no auth/TLS on the HTTP endpoint. Test signals: missing/corrupt TDB, profile fixtures, per-service labels with special characters, status codes, Prometheus format validation, and descriptor cleanup on failures.
