# sources/storage-engines/tikv/src/server/service/diagnostics/log.rs

Purpose: implements Diagnostics log search over normal and rotated TiKV log files with time, level, and regex filtering, producing batched streaming responses.

Important APIs/types/functions: `LogIterator`; `Error`; `search`; `is_log_file`; `parse_time`; `parse_level`; `parse`; `parse_time_range`; `batch_log_item`.

Control flow: `LogIterator::new` scans the log directory for normal/rotated files whose stems match the base log path, parses file start/end times from valid edge lines, filters by requested range, sorts by start time, and prepares line iteration. `next` parses TiKV log headers, attaches malformed/continuation lines to the previous valid log metadata, enforces range/level/regex filters, and yields `LogMessage`. `search` compiles regexes, builds level bitmask, handles missing log file as empty, and batches 256 messages per `SearchLogResponse`.

State/persistence: read-only filesystem access. No tailing or writes.

Dependencies/integration: called by diagnostics gRPC service; depends on chrono, nom, regex, rev_lines, itertools, futures streams, and diagnostics protobufs. Risks include unwraps on file stems, skipping malformed-edge files due to 10-line parse limit, expensive user regexes, and inherited metadata for invalid lines. Tests cover parsers, time ranges, iterator filters, rotated names, and search stream.
