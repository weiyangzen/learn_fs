<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/checkpatch.conf -->
# sources/user-network-fs/nfs-ganesha/src/scripts/checkpatch.conf

## Purpose
This file configures Linux `checkpatch.pl` for the NFS-Ganesha codebase, disabling kernel-specific checks and adjusting style policy to match a user-space NFS server rather than the Linux kernel tree.

## Important APIs, Types, and Functions
The file is a list of checkpatch flags. `--no-tree` tells checkpatch this is not a kernel tree. Many `--ignore` entries disable kernel-only errors/warnings (`MODIFIED_INCLUDE_ASM`, `UAPI_INCLUDE`, `LOCKDEP`, `EXPORT_SYMBOL`, `PRINTK_*`, etc.), project-accepted style deviations (`CAMELCASE`, `UNNECESSARY_ELSE`, `BRACES`, `SPLIT_STRING`, `SYMBOLIC_PERMS`, `FUNCTION_ARGUMENTS`, `COMPLEX_MACRO`, `MACRO_WITH_FLOW_CONTROL`, `POINTER_LOCATION`, `SPACING`, `INDENTED_LABEL`), and metadata checks (`GERRIT_CHANGE_ID`, `FSF_MAILING_ADDRESS`, `GIT_COMMIT_ID`). It sets `--max-line-length=80`.

## Control Flow
There is no runtime control flow. Checkpatch reads these options and suppresses matching diagnostics when run by project scripts such as `runcp.sh`.

## State and Persistence Behavior
It persists style policy in the repository. It does not modify source files by itself.

## Dependencies and Integration Points
It depends on Linux `checkpatch.pl` option names remaining stable. It integrates with developer/CI style checks and the scripts directory tooling.

## Risks and Edge Cases
The broad ignore list can hide real maintainability issues, especially around complex macros, spacing, pointer location, and date/time usage. One line has a leading space before `--max-line-length=80`; parsers generally tolerate whitespace, but exact tooling should be checked. Duplicate ignores such as `DATE_TIME` are harmless but indicate drift. Misspellings in comments do not affect behavior.

## Test Signals
Style-check tests should run checkpatch with this config on known-good and known-bad patches, verifying that intended project exceptions are suppressed while important non-ignored errors still fail.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/checkpatch.conf -->
