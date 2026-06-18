<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_pre_push.go -->
# sources/sync-backup/git-lfs/commands/command_pre_push.go

Purpose: implements the Git `pre-push` hook command, uploading required LFS objects for pushed ref updates before Git completes the push.

Important APIs/types/functions: global `prePushDryRun`; `prePushCommand`, `prePushRefs`, and `decodeRefs`; `git.MapRemoteURL`, `cfg.SetValidPushRemote`, `newUploadContext`, and `uploadForRefUpdates`.

Control flow: validates hook args, respects `GIT_LFS_SKIP_PUSH`, validates Git version, maps the remote argument to a configured remote, creates upload context, parses stdin lines of `<local ref> <local sha> <remote ref> <remote sha>`, skips branch deletions with zero local SHA, creates `git.RefUpdate` values, and uploads objects for those updates.

State and persistence behavior: contacts LFS upload endpoint and may update transfer/log state; no local working-tree mutation. Dry-run avoids actual upload via upload context.

Dependencies/integration points: depends on Git pre-push stdin contract, remote URL mapping, upload context implementation, and lock verification in upload flow.

Risks and test signals: risks include scanner errors ignored in `prePushRefs`, simplistic space splitting, remote mapping edge cases, and environment skip bypassing all validation. Test signals include single/multiple updates, deleted branch skip, dry-run, invalid remote, URL-mapped remote, stdin blank lines, and upload failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_pre_push.go -->
