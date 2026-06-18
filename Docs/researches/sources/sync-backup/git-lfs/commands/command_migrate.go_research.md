<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate.go -->
# sources/sync-backup/git-lfs/commands/command_migrate.go

Purpose: shared implementation and command registration for `git lfs migrate` subcommands, especially ref selection, working-copy safety, history rewriter setup, and global migrate flags.

Important APIs/types/functions: globals `migrateIncludeRefs`, `migrateExcludeRefs`, `migrateYes`, `migrateSkipFetch`, `migrateImportAboveFmt`, `migrateEverything`, `migrateVerbose`, `objectMapFilePath`, `migrateNoRewrite`, `migrateCommitMessage`, `exportRemote`, `migrateFixup`; functions `migrate`, `getObjectDatabase`, `rewriteOptions`, `isSpecialGitRef`, `includeExcludeRefs`, `getRemoteRefs`, `fetchRemoteRefs`, `formatRefName`, `currentRefToMigrate`, `getHistoryRewriter`, and `ensureWorkingCopyClean`.

Control flow: command registration wires `info`, `import`, and `export` subcommands. `migrate` sets up the repository, computes rewrite options from args and flags, and calls `githistory.Rewriter.Rewrite`. Ref selection defaults to current local ref, supports explicit args and include/exclude refs, excludes remote refs in non-bare default mode, and with `--everything` includes local branches/tags, remote branches, and non-special other refs while excluding stash/notes/bisect/replace. Dirty worktrees prompt unless `--yes`.

State and persistence behavior: opens the Git object database rooted at common dir and uses temp storage. It may fetch remote refs unless `--skip-fetch`, prompts on stdin/stdout, and later subcommands rewrite refs through provided options.

Dependencies/integration points: central integration with `git/githistory`, `gitobj`, Git remote/ref APIs, filepath filters in Git attributes mode, tasklog, and migrate subcommand-specific blob/tree callbacks.

Risks and test signals: risks include a likely bug in `strings.HasPrefix("^", name)` instead of checking the name for `^`, destructive dirty-worktree override after prompt, ref namespace edge cases, and remote fetch dependence. Test signals include default current branch migration, `--everything`, include/exclude refs, special ref exclusion, dirty prompt yes/no/EOF, skip-fetch using cached refs, and non-local current ref rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_migrate.go -->
