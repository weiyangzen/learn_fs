# sources/sync-backup/git-lfs/t/t-credentials-no-prompt.sh

## Purpose
Tests non-interactive credential failure behavior. It ensures Git LFS does not hang for prompts when `GIT_TERMINAL_PROMPT=0` and credential helpers or askpass commands cannot supply usable credentials.

## Important APIs, Functions, and Control Flow
The first test configures `credential.helper lfsnoop` globally and locally, then pushes without credentials and expects an authorization or missing-credentials error. The second disables credential helpers, sets a nonexistent `GIT_ASKPASS`, blocks terminal prompts, and expects both an askpass failure and a credential fill attempt.

## State, Persistence, and Dependencies
State includes global/local credential config, committed LFS files, and `push.log`. The script depends on Git version `>= 2.3.0`, `git-credential-lfsnoop`, and prompt suppression through `GIT_TERMINAL_PROMPT=0`.

## Integration Points, Risks, and Test Signals
Integration is with Git credential lookup and prompt suppression. Signals are explicit authorization/missing-credential messages, `failed to find GIT_ASKPASS command`, and `creds: git credential fill`. Risks are version-specific credential behavior and multiple accepted error strings in the first test.
