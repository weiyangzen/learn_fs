## sources/test-tools/syzkaller/pkg/log/log.go

Purpose: syzkaller-wide logging helpers with verbosity levels, optional instance name, fatal/error helpers, in-memory recent log caching, and a verbose writer adapter.

Important APIs/types/functions: global `-vv` flag, `EnableLogCaching`, `CachedLogOutput`, `SetName`, `V`, `Log`, `Logf`, `Error/Errorf`, `Fatal/Fatalf`, `message`, `writeMessage`, and `VerboseWriter`.

Control flow: `Logf` lazily formats only if verbosity or cache needs the message. Cache stores a ring of recent messages, prunes by max memory, and optionally prepends time. Fatal delegates to standard log fatal after formatting.

State and persistence: global mutex-protected cache, atomic cache enable flag, global instance name, and verbosity flag. Output goes to standard logger.

Dependencies and integration: used across packages for global logging and recent output capture.

Risks: `EnableLogCaching` is one-shot and fatal if called twice. Global state makes tests/order sensitive. Cache memory accounting is by string length and intentionally simple.

Test signals: `log_test.go` validates cache ring/memory trimming and lazy formatting.
