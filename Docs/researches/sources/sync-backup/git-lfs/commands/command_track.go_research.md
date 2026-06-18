<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_track.go -->
# sources/sync-backup/git-lfs/commands/command_track.go

Purpose: implements `git lfs track`, listing or modifying Git attributes patterns for LFS tracking and lockable behavior.

Important APIs/types/functions: blocklist `prefixBlocklist`; flags `trackLockableFlag`, `trackNotLockableFlag`, `trackVerboseLoggingFlag`, `trackDryRunFlag`, `trackNoModifyAttrsFlag`, `trackNoExcludedFlag`, `trackFilenameFlag`, `trackJSONFlag`; `trackCommand`, `PatternData`, `listPatterns`, `getAllKnownPatterns`, `getAttributeLineEnding`, `blocklistItem`, `escapeGlobCharacters`, `escapeAttrPattern`, and `unescapeAttrPattern`.

Control flow: validates Git version and working copy, optionally installs hooks, lists patterns when no args, rejects JSON with modifications, loads system/user/local attributes for macro expansion and line endings, computes cwd relative to repo root, normalizes/escapes each pattern, skips already-supported patterns, prepares changed `.gitattributes` lines, rewrites existing local `.gitattributes`, appends new patterns after checking Git-tracked matches and blocklisted `.git`/`.lfs` files, touches matching tracked files to mark them modified, then fixes lockable file write flags.

State and persistence behavior: writes `.gitattributes`, changes mtimes of matching tracked files, and mutates file permissions for lockable/not-lockable changes. Dry-run disables attributes modification and avoids touching mtimes.

Dependencies/integration points: integrates Git attributes parser/macro processor, hook installation, Git tracked-file lookup, path cleanup helpers, lock client permission fixes, config line endings, and JSON encoder.

Risks and test signals: risks include map iteration ordering for appended patterns, broad extension/glob escaping differences by platform, blocklist only checking tracked matches, `.gitattributes` truncation before full write, and global flags for lockable/not-lockable conflict not explicitly rejected. Test signals include listing text/JSON, tracking new/existing patterns, dry-run, no-modify-attrs, filename literal escaping, lockable/not-lockable permissions, subdirectory execution, line-ending preservation, and forbidden file match.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_track.go -->
