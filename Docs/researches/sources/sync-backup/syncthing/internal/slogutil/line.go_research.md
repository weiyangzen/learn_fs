# sources/sync-backup/syncthing/internal/slogutil/line.go

Purpose: Defines the internal log-line representation used by the formatter, in-memory recorders, and API responses.

Important APIs/types/functions: `Line` contains `When`, `Message`, and `Level`. `WriteTo` renders optional syslog priority, timestamp, level string, message, and newline. `levelStr` maps slog levels to `DBG`, `INF`, `WRN`, and `ERR`, preserving numeric offsets. `syslogPriority` maps levels to syslog priorities. `MarshalJSON` emits short level strings instead of slog's default numeric encoding.

Control flow: Rendering builds a buffer and writes it to the supplied writer. JSON marshaling constructs a small map with the custom level string.

State and persistence behavior: A `Line` is immutable-by-convention value state for logs. No persistence is performed here; recorders and API handlers store or expose it.

Dependencies and integration points: Used by `formattingHandler`, `lineRecorder`, `/rest/system/log`, `/rest/system/error`, and support bundles.

Risks: JSON output uses a map, so field ordering is not part of the contract. The syslog priority mapping is simple and should be kept consistent with operational logging expectations.

Test signals: Covered indirectly by `formatting_test.go` and API log endpoint tests.
