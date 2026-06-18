# sources/sync-backup/git-lfs/git/rev_list_scanner_test.go

Purpose: tests `revListArgs` construction and `RevListScanner` parser/close behavior.

Important APIs/types/functions: `ArgsTestCase`, `revListArgs`, `RevListScanner.Close`, `Scan`, `OID`, `Name`, and `ScanRefsOptions`.

Control flow: many cases assert expected stdin and Git args for scan modes, skip-deleted, remote ranges, skipped refs, order flags, commits-only, reverse, and unknown mode errors. Additional tests assert optional close function behavior and parsing lines with or without names.

State/persistence behavior: in-memory only; no Git subprocess is launched in these tests.

Dependencies/integration: provides contract coverage for LFS scanners and history rewriter callers that rely on exact rev-list flags.

Risks/test signals: does not test real `git rev-list` close errors, ambiguous warnings, zero SHA filtering assertions directly, or large output.
