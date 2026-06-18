<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/rsync-no-vanished -->
# sources/sync-backup/rsync/support/rsync-no-vanished

Purpose: bash wrapper around `/usr/bin/rsync` that suppresses vanished-file warnings and treats rsync exit code 24 as success for client runs.

Important APIs/types/functions: constants `REAL_RSYNC`, `IGNOREEXIT=24`, and `IGNOREOUT` regex. No functions are defined.

Control flow: if any argument is `--server`, immediately exec real rsync so server-side protocol is untouched. Otherwise enable `pipefail`, run rsync with stderr piped through `grep -E -v` while preserving stdout on its original stream, capture rsync's pipeline status, map return code 24 to 0, and exit with the adjusted code.

State and persistence behavior: no persistent state; it filters process output.

Dependencies and integration points: depends on bash arrays/process redirection, grep, and rsync exit-code semantics. It can be installed under another name or even as `rsync` because server mode is bypassed.

Risks: filtering is regex-based and may hide lines that match the vanished pattern but matter in context. Only code 24 is remapped. Quoting around `$REAL_RSYNC` assumes the path has no spaces.

Test signals: vanished-file scenarios should produce zero exit and filtered stderr; unrelated warnings/errors should remain visible and preserve nonzero exit. Server-mode invocation must exec real rsync without filtering.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/rsync-no-vanished -->
