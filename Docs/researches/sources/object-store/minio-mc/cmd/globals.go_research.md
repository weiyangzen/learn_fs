# sources/object-store/minio-mc/cmd/globals.go

Purpose: Defines process-wide constants, global runtime settings, root context, terminal/pager state, and global flag application.

Important APIs/types/functions: config/session constants, global booleans/rates/context variables, `parsePagerDisableFlag`, and `setGlobalsFromContext`.

Control flow: `setGlobalsFromContext` merges local and global CLI flags, turns off color for no-color/quiet/json-line output, parses connection deadlines, upload/download limits, DNS resolve overrides, and custom HTTP headers with validation.

State and persistence: Mutates package-level globals used by clients, output, network transport, and cancellation. No persistence to disk.

Dependencies/integration: Used by nearly every command through `Before: setGlobalsFromContext`. Depends on console/lipgloss, humanize, netip, HTTP header validation, and madmin types.

Risks: Global mutable state can leak between tests and commands in the same process. Accumulative `globalQuiet = globalQuiet || quiet` style means flags only turn on, not off.

Test signals: No direct tests.
