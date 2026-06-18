# sources/sync-backup/git-lfs/subprocess/subprocess.go

Purpose: central subprocess helper package for command execution, shell quoting, trace logging, and sanitized environment construction.

Important APIs/functions: `BufferedExec`, `StdoutBufferedExec`, `SimpleExec`, `Output`, `ShellQuoteSingle`, `ShellQuote`, `FormatForShell`, `FormatForShellQuotedArgs`, `FormatPercentSequences`, `Trace`, `quotedArgs`, `fetchEnvironment`, `fetchEnvironmentInternal`, and `ResetEnvironment`.

Control flow: exec helpers construct `Cmd`, create pipes/readers, start processes, and return wrappers. `Output` normalizes successful stdout trimming and expands `exec.ExitError` into a command/error-output message. Quoting helpers produce shell-safe single-quoted args. Environment fetching caches `os.Environ` minus `GIT_TRACE` and `GIT_INTERNAL_SUPER_PREFIX`.

State/persistence behavior: package-level cached environment guarded by `envMu`; resettable for tests or environment changes.

Dependencies/integration: used broadly by Git LFS for Git commands, SSH commands, and custom tool execution.

Risks: `FormatForShell` intentionally does no quoting and should be avoided with untrusted args. Cached environment can become stale unless `ResetEnvironment` is called after env changes. `Output` discards stdout on nonzero exit by design.

Test signals: `subprocess_test.go` covers quoting, shell command formatting, and percent sequence replacement.
