# sources/security-integrity/fscrypt/cmd/fscrypt/prompt.go

## Purpose
Handles interactive and quiet-mode prompts for confirmations, protector source/name selection, key files, and protector choice.

## APIs, Types, and Control Flow
`askQuestion` loops for yes/no input and defaults in quiet mode. `askConfirmation` honors `--force`, rejects destructive default-no prompts in quiet mode, prints warnings, and returns `ErrCanceled` on no. `usernameFromID`, `formatUsername`, and `formatInfo` provide display text for protector metadata. `promptForName` uses flag or prompt, skipping login protectors. `promptForSource` uses flag, quiet default, or numbered source list. `promptForKeyFile` uses flag, quiet error, or repeated file prompt. `promptForProtector` filters load errors, auto-selects a sole option, rejects quiet ambiguity, displays linked protector origin, and returns a selected index. `optionFn` implements `--unlock-with` matching or delegates to prompt selection.

## State, Dependencies, and Integration
Relies on global flags and `util.ReadLine`. It is central to CLI-to-action callbacks and user-visible status descriptions.

## Risks and Test Signals
Quiet mode defaults can silently select defaults or reject ambiguous actions. `promptForProtector` allows selecting an index with load error if manually entered, because the validation checks only range; later callers return the load error. CLI expect tests cover prompt text and flows.
