<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/password.go -->
# sources/sync-backup/kopia/cli/password.go

## Purpose
Provides shared repository password prompting and selection logic, including create/change/existing prompts, flag/persistent precedence, and file descriptor conversion.

## Important APIs, Types, And Functions
Key functions are `askForNewRepositoryPassword`, `askForChangedRepositoryPassword`, `askForExistingRepositoryPassword`, `setPasswordFromToken`, `getPasswordFromFlags`, `askPass`, and `intFd`.

## Control Flow
`getPasswordFromFlags` prefers `--password`/environment value, prompts twice for create, tries persistent password storage when allowed, and falls back to one existing-password prompt. `askPass` uses terminal password input up to five non-empty attempts.

## State And Persistence Behavior
No repository data is changed here, but selected passwords unlock or create repository state. Passwords are held in memory as strings. Persistent lookup is delegated to password persistence strategy.

## Dependencies And Integration Points
Integrates terminal FD handling, `golang.org/x/term`, password persistence errors, and App IO streams.

## Risks And Edge Cases
Interactive prompting requires `os.Stdin` to be a valid terminal-like file descriptor, which can fail in noninteractive contexts. Empty passwords are silently retried up to five times. `askForChangedRepositoryPassword` prints mismatch to global stdout instead of the provided writer.

## Test Signals
Tests should cover flag precedence, persistent fallback, prompt retry/mismatch, nonterminal errors, and FD overflow handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/password.go -->
