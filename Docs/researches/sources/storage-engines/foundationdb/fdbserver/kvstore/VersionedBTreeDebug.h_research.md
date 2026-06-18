# sources/storage-engines/foundationdb/fdbserver/kvstore/VersionedBTreeDebug.h

## Purpose
This header declares Redwood/VersionedBTree debug facilities and macros used throughout the storage engine. It allows expensive debug output to be compiled out by default while still providing always-on emergency tracing helpers.

## Important APIs, Types, And Functions
The public surface is `g_debugStream`, `g_allowXOREncryptionInSimulation`, `enableRedwoodDebug()`, and macros `debug_printf_always`, `debug_print`, `debug_print_always`, `debug_printf`, `debug_printf_noop`, `BEACON`, and `TRACE`. `REDWOOD_DEBUG` is set to `0`, so debug printing normally compiles to a no-op under `NO_INTELLISENSE`.

## Control Flow
`debug_printf_always` formats a prefix containing local network address, current time, and source line, prefixes every message line with `addPrefix`, writes to `g_debugStream`, and flushes. `debug_printf` either wraps `debug_printf_always` with `enableRedwoodDebug()` or becomes `debug_printf_noop`. IDE builds can map it to `printf` for format checking.

## State And Persistence Behavior
The header itself owns no state but exposes globals implemented in the `.cpp`. Debug lines are flushed synchronously to a `FILE*`; this can affect timing when enabled and can interleave across callers.

## Dependencies And Integration Points
It depends on Flow formatting, network, time, and `platform::get_backtrace()`. It integrates with VersionedBTree/Redwood internals as a low-friction debugging layer and with simulation via the XOR-encryption knob.

## Risks And Test Signals
Macro bodies evaluate formatting arguments only when active, so side-effecting arguments can behave differently across builds. `debug_printf_always` assumes `g_network` is usable. Build tests should cover normal compiled-out mode, format-checking mode, and a debug-enabled build that validates prefixing and flush behavior.
