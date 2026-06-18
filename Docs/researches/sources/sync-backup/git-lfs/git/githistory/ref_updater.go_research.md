# sources/sync-backup/git-lfs/git/githistory/ref_updater.go

Purpose: updates refs after history rewriting, including lightweight and annotated tag handling.

Important APIs/types/functions: `refUpdater`, `updateRefs`, `updateOneTag`, and `updateOneRef`.

Control flow: `updateRefs` opens `git update-ref --stdin`, optionally starts a transaction for Git 2.27+, deduplicates seen refspecs, calls `updateOneRef` for each ref, then prepares/commits and waits for the command. `updateOneRef` maps the ref SHA through `cacheFn`; for tag refs it may rewrite tag objects, recursively update inner annotated tags, and then writes NUL-delimited update commands.

State/persistence behavior: writes new tag objects to the object database and moves refs in the repository, creating reflog entries through Git. Progress is logged through `tasklog`.

Dependencies/integration: integrates with `git.UpdateRefsFromStdin`, `git.ResolveRef`, `git.Ref`, `gitobj.Tag`, Git version detection, and `Rewriter` commit cache.

Risks/test signals: annotated tag handling is subtle; missing cached objects leave refs untouched. Any command stdin/transaction formatting regression can move no refs or fail the whole update. Tests cover moving lightweight tags, annotated tags, and ignoring unmapped refs.
