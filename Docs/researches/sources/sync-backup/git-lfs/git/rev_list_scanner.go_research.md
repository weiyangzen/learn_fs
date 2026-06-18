# sources/sync-backup/git-lfs/git/rev_list_scanner.go

Purpose: constructs and parses `git rev-list` scans for objects or commits across include/exclude refs, all refs, or ranges relative to remotes.

Important APIs/types/functions: `ScanningMode`, `RevListOrder`, `ScanRefsOptions`, `RevListScanner`, `NewRevListScanner`, `revListArgs`, `includeExcludeShas`, `nonZeroShas`, `Scan`, `OID`, `Name`, `Err`, and `Close`.

Control flow: argument construction adds `--objects` unless commits-only, reverse/order flags, mode-specific traversal flags and stdin content, then runs `git rev-list --stdin --`. The scanner parses each output line, extracts a leading object ID via regex, decodes it, and stores any trailing name. `Close` waits on the command and promotes ambiguous-ref warnings to errors.

State/persistence behavior: subprocess-backed read-only scan. `ScanRefsOptions.Names` can be shared across goroutines with a mutex.

Dependencies/integration: used by `githistory.Rewriter` for topological commit selection and by LFS ref scanners for object discovery.

Risks/test signals: scanner buffer is default `bufio.Scanner` size; very long path lines could be an issue. Ambiguous refs are treated as fatal only at `Close`, so callers must close. Tests cover args, close behavior, and line parsing.
