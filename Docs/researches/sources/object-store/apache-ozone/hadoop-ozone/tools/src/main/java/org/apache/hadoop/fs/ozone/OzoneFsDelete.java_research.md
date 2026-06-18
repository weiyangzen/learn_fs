# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/fs/ozone/OzoneFsDelete.java

## Purpose
Ozone-specific delete command registrations and implementations for Hadoop FsShell, overriding standard `-rm` behavior where Ozone symlink and URI semantics differ.

## Important APIs, types, and functions
`registerCommands` binds `-rm` and `-rmr`. `Rm` extends `FsCommand` and implements option parsing, argument expansion, path processing, trash handling, and safe-delete prompts. `Rmr` prepends `-r` and reports replacement command `-rm -r`.

## Control flow
`processOptions` parses `-f`, `-r`, `-R`, `-skipTrash`, and `-safely`. `expandArgument` records trailing slash and suppresses missing paths under `-f`. `processPath` detects symlinks, rejects directories without recursion, preserves Ozone trailing-slash behavior for symlink bucket contents, tries Trash unless skipped, optionally confirms large recursive deletes, then calls `FileSystem.delete`.

## State and persistence behavior
The command mutates filesystem namespace state by moving paths to Trash or deleting them. It reads content summary for safety checks and consults Hadoop delete-limit configuration.

## Dependencies and integration points
Integrates Hadoop shell classes, `Trash`, `PathData`, `ContentSummary`, Ozone URI delimiter semantics, and `ToolRunner.confirmPrompt`.

## Risks and edge cases
The `trailing` flag is command-instance state and can affect later paths after any trailing-slash argument. Symlink detection depends on `getLinkTarget(item.path) != item.path`, which is object-identity-sensitive. Trash failures are rewrapped with `-skipTrash` guidance.

## Test signals
Direct tests in this subset check command registration. Behavioral signals would include directory rejection, missing-file `-f`, trash fallback, safe-delete prompt behavior, and symlink trailing slash deletes.
