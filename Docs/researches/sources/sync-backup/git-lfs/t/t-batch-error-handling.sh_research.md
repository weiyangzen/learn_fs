# sources/sync-backup/git-lfs/t/t-batch-error-handling.sh

## Purpose
Tests client behavior when the batch API returns a malformed or unexpected HTTP response. The repository name `badbatch` is a test-server trigger for an abnormal 203 response.

## Important APIs, Functions, and Control Flow
The test creates a remote and two clones, tracks `*.dat`, commits `a.dat`, verifies the committed Git object is an LFS pointer, verifies the server initially lacks the object, then attempts `git push origin main`. The expected flow ends in a parse error rather than a successful upload.

## State, Persistence, and Dependencies
State includes a local commit, `.gitattributes`, a missing server-side LFS object, and `push.log`. It depends on `setup_remote_repo`, `clone_repo`, `calc_oid`, `assert_pointer`, and `refute_server_object`.

## Integration Points, Risks, and Test Signals
The integration point is batch API response parsing during push. The key signal is `Unable to parse HTTP response` in `push.log`. Risks are high coupling to test-server behavior keyed by repository name and exact user-facing error text.
