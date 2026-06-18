# sources/sync-backup/git-lfs/t/t-askpass.sh

## Purpose
Credential integration tests for Git LFS askpass fallback. The script validates precedence and behavior for `GIT_ASKPASS`, `core.askPass`, `SSH_ASKPASS`, bad credentials, 401/403 responses, and credentials embedded in remote URLs.

## Important APIs, Functions, and Control Flow
Each test creates a remote repository, tracks `*.dat`, commits an LFS object, disables credential helpers when needed, sets askpass-related environment variables, and pushes. Success cases assert `main -> main`; failure cases assert absence of successful upload and match authorization messages or authentication-attempt limits. The final test rewrites `remote.origin.url` to include `user:pass` and ensures askpass is not invoked.

## State, Persistence, and Dependencies
The tests depend on `lfs-askpass`, `LFS_ASKPASS_USERNAME`, `LFS_ASKPASS_PASSWORD`, `GIT_TRACE`, and `GIT_CURL_VERBOSE`. They mutate local Git config (`credential.helper`, `core.askPass`, remote URL) and inspect `push.log`.

## Integration Points, Risks, and Test Signals
Integration is with Git credential prompting and the Git LFS HTTP client. Signals include trace lines `filling with GIT_ASKPASS`, request counts for username/password prompts, authorization error text, and `refute_server_object` for failed uploads. Risks include Git version or platform differences in prompt ordering and trace formatting.
