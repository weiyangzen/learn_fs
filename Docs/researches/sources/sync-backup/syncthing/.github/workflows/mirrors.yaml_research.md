# sources/sync-backup/syncthing/.github/workflows/mirrors.yaml

Purpose: mirrors the GitHub repository to Codeberg on push and delete events.

Important APIs/types/functions: job `codeberg` checks out full history and uses `yesolutions/mirror-action` with `REMOTE`, `GIT_SSH_PRIVATE_KEY`, and host verification disabled.

Control flow: when the repository owner is `syncthing`, checkout fetches all refs, then the mirror action pushes changes or deletions to the Codeberg remote.

State and persistence behavior: no local state. Persistent state is the remote mirrored Git repository.

Dependencies/integration: depends on `secrets.CODEBERG_PUSH_KEY`, SSH reachability to Codeberg, and the mirror action revision.

Risks/test signals: `GIT_SSH_NO_VERIFY_HOST: true` trades host verification for automation convenience. Mirror failures may leave Codeberg stale. Signal is Codeberg refs matching GitHub after push/delete events.
