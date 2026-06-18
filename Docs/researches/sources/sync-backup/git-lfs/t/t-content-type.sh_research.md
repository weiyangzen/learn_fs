# sources/sync-backup/git-lfs/t/t-content-type.sh

## Purpose
Tests Content-Type detection for LFS uploads and the warning emitted when a server rejects unsupported content types.

## Important APIs, Functions, and Control Flow
The first test creates a `.tar.gz` LFS object and expects `Content-Type: application/x-gzip` in curl verbose upload output by default. The second sets `lfs.$GITSERVER.contenttype 0` and expects `application/octet-stream` instead. The third uploads content `status-storage-422`, which triggers server rejection and verifies user guidance to disable content-type detection.

## State, Persistence, and Dependencies
State includes local Git config, tar-generated files, push logs, and server object behavior. Dependencies include `tar`, `GIT_CURL_VERBOSE`, repository-name/content triggers, and `git lfs track`.

## Integration Points, Risks, and Test Signals
Integration is with MIME detection and upload request header construction. Signals are curl verbose header counts and warning text. Risks are platform-dependent MIME detection and exact server-triggered message wording.
