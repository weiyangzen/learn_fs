<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_push.go -->
# sources/sync-backup/git-lfs/commands/command_push.go

Purpose: implements user-facing `git lfs push`, uploading LFS objects by ref comparison, all local refs, explicit object IDs, or stdin-provided refs/OIDs.

Important APIs/types/functions: globals `pushDryRun`, `pushObjectIDs`, `pushAll`, `useStdin`; `pushCommand`, `uploadsBetweenRefAndRemote`, `uploadsWithObjectIDs`, and `lfsPushRefs`; `newUploadContext`, `uploadForRefUpdates`, `git.LocalRefs`, and `git.NewRefUpdate`.

Control flow: requires a remote arg, validates Git version and push remote, gathers remaining args or stdin lines, then either validates and uploads explicit object IDs by statting local media files, or resolves ref updates from local refs/explicit names/all refs and delegates upload scanning. It reports invalid input with exit code 1 or fatal upload errors through shared error handling.

State and persistence behavior: uploads local media to the LFS server; reads object files and refs; no working-tree mutation. Dry-run configures upload context not to send data.

Dependencies/integration points: depends on upload context implementation, transfer queues, push remote config, local refs, object path layout, and shared `useStdin` global also used by fetch in a different file name.

Risks and test signals: risks include explicit object ID mode trusting local object size from filesystem, ref lookup only by local ref name before falling back to resolve, and `--all` with explicit refs behavior. Test signals include remote required, invalid remote, stdin refs, stdin OIDs, object-id missing file, push all, explicit branch/tag/SHA, dry-run, and upload errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_push.go -->
