<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testingaction/main.go -->
# sources/sync-backup/kopia/tests/testingaction/main.go

This file implements a small command used by tests to simulate external actions. It parses flags for output files, delays, copied file specs, and input/output behavior, then writes/copies data accordingly.

Important functions are `main`, `writeFileTo`, `copyFiles`, and `copyFile`. Control flow can sleep, copy files described by a spec file, write named files to stdout/stderr, and copy byte streams. It uses scanner/line parsing for specs.

State is filesystem side effects and process stdout/stderr. Dependencies are standard I/O and flags only. Risks include broad file path access from spec input, scanner limits for long spec lines, and test hangs if delay values are large. Test signals are indirect from command/action integration tests that invoke this helper binary.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testingaction/main.go -->
