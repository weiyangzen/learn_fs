# Research: sources/object-store/minio-mc/cmd/progress-bar.go

## sources/object-store/minio-mc/cmd/progress-bar.go

Purpose: wraps `cheggaaa/pb` progress bars for byte-oriented transfers and caption formatting.

Important APIs and types: `progressBar` embeds `*pb.ProgressBar`; `newPB`, `newProgressReader`, `newProgressBar`, `SetCaption`, `Finish`, `Set64`, `Read`, `SetTotal`, `cursorAnimate`, `fixateBarCaption`, and `getFixedWidth`.

Control flow: `newPB` configures byte units, refresh rate, no automatic newline, speed display, and a colorized callback. `newProgressReader` returns a proxy reader with optional fixed caption. `Read` delegates to pb and clamps progress to total after retries. Caption functions fit display text to a percentage of terminal width.

State and persistence: no durable state; progress state is in memory and terminal output.

Dependencies and integration: used by `put`, `pipe`, `mirror` status implementations, and other transfer flows. Depends on global terminal width and console colorization.

Risks and tests: `cursorAnimate` starts an endless goroutine for every call. Caption truncation uses byte length rather than display width. No direct progress-bar tests in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/progress-bar.go -->
