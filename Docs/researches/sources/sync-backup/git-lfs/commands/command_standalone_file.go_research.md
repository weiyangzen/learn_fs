<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_standalone_file.go -->
# sources/sync-backup/git-lfs/commands/command_standalone_file.go

Purpose: implements `git lfs standalone-file`, processing standalone transfer adapter data from stdin to stdout.

Important APIs/types/functions: `standaloneFileCommand` and `standalone.ProcessStandaloneData`.

Control flow: delegates directly to standalone file processor with current config and standard streams, exiting through shared error handling on failure.

State and persistence behavior: behavior is owned by the standalone package; this command streams data and may read/write local object data according to standalone transfer protocol.

Dependencies/integration points: integrates the `lfshttp/standalone` adapter with Cobra command registration and global config.

Risks and test signals: risks are mostly delegated: protocol framing, stdin/stdout binary safety, and config availability. Test signals include valid standalone transfer requests over stdin/stdout and propagated processing errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_standalone_file.go -->
