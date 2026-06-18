# sources/sync-backup/git-lfs/t/t-credentials.sh

## Purpose
Large credential integration suite for Git LFS. It covers credential helper precedence, `useHttpPath`, 401/403 retry behavior, WWW-Authenticate forwarding, Bearer and multistage auth capabilities, raw `git credential` helper behavior, netrc fallback, credentials in `lfs.url`, and credentials in `remote.origin.url`.

## Important APIs, Functions, and Control Flow
The file sets `CREDSDIR` and `setup_creds`, then creates per-test repositories and credential records. Tests push LFS objects under different helper and config settings, count `git credential fill/approve/reject/cache`, validate path inclusion or omission, and verify object presence or absence. Netrc tests iterate `.netrc` and `_netrc` on Windows. URL credential tests switch between bad unauthenticated URLs and embedded `requirecreds:pass` credentials, checking storage endpoint access-mode behavior.

## State, Persistence, and Dependencies
State includes credential record files, `.netrc`, Git global/local config, credential capability output, `LFS_TEST_CREDS_WWWAUTH`, remote URLs, LFS object caches, and trace/curl logs. Dependencies include `git-credential-lfstest`, `git credential capability`, server auth modes, `setup_remote_repo`, and object assertions.

## Integration Points, Risks, and Test Signals
Integration points are Git credential plumbing, LFS API authentication retries, locking API authentication, WWW-Authenticate metadata, netrc parsing, auth-state capabilities, and endpoint access-mode caching. Signals are upload progress or absence, fill/approve counts, authorization headers, retry-limit messages, credential output exact matches, and object-store assertions. Risks include Git version capability differences, global config pollution, platform netrc naming, and exact trace log matching.
