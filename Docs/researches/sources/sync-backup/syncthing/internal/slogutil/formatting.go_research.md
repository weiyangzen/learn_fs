# sources/sync-backup/syncthing/internal/slogutil/formatting.go

Purpose: Syncthing's custom `slog.Handler` that formats log records into the legacy human-readable line style while preserving structured attributes for expansion and recording.

Important APIs/types/functions: `LineFormat` controls timestamp, textual level, and syslog priority rendering. `formattingOptions` carries output writer, recorders, and a test time override. `formattingHandler` implements `slog.Handler` with `Enabled`, `Handle`, `WithAttrs`, and `WithGroup`. `SetLineFormat` mutates the global formatter. Helpers include `expandAttrs`, `appendAttr`, and `funcNameToPkg`.

Control flow: `Handle` derives package/type/source information from `rec.PC`, checks package log level through `globalLevels`, appends package/source log attributes, prefixes grouped attrs, expands nested slog groups into dotted keys, quotes confusing or empty values, records the final `Line`, and writes it to the configured writer. `WithAttrs` applies active group prefixes to new attrs, while `WithGroup` prepends group names for later prefixing.

State and persistence behavior: Global formatting state lives in `globalFormatter`; in-memory log lines are copied into configured `lineRecorder`s. There is no disk persistence in this handler.

Dependencies and integration points: Depends on `runtime.CallersFrames`, `log/slog`, `Line`, `lineRecorder`, and the package-level log tracker. It is installed as the default slog handler by `sloginit.go` and feeds API log endpoints through recorders.

Risks: `SetLineFormat` mutates global state without synchronization. `WithGroup` prepends group names, which produces the observed `bar.foo` order for nested groups and is a compatibility behavior to preserve. Function-name parsing assumes Syncthing package path conventions. Attribute formatting is lossy compared with structured JSON logs.

Test signals: `formatting_test.go` verifies quoting, grouping, level filtering, package metadata, and debug filtering at default info level.
