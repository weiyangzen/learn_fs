<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/printer.go -->
# sources/sync-backup/restic/internal/ui/progress/printer.go

## Purpose
Defines the generic progress printer interface used by commands and provides a no-op implementation.

## Important APIs and Control Flow
`Printer` includes counter creation and severity/verbosity printing methods; `NewNoopPrinter` returns a `noopPrinter` whose methods discard output and counters use core no-op counters. Control flow is interface dispatch only; no-op methods intentionally do nothing.

## State, Persistence, Dependencies, and Integration
No persistent state. It decouples command code from terminal-specific printers and lets tests disable output.

## Risks and Test Signals
Risks are interface drift and nil/no-op behavior hiding missing output in tests. Compile-time conformance and UI tests provide signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/printer.go -->
