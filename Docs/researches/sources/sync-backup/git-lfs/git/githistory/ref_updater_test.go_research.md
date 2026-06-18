# sources/sync-backup/git-lfs/git/githistory/ref_updater_test.go

Purpose: tests `refUpdater` ref movement behavior for lightweight tags, annotated tags, and unmapped refs.

Important APIs/types/functions: `DatabaseFromFixture`, `AssertRef`, `refUpdater.updateRefs`, `git.Ref`, and fixed `cacheFn` closures.

Control flow: each test copies a fixture, asserts the initial tag ref, constructs a `refUpdater`, runs `updateRefs`, and asserts final ref state. Annotated tag case expects a newly written tag object SHA rather than the raw commit SHA.

State/persistence behavior: mutates refs in temp fixture copies via `git update-ref`. Object database may receive new tag objects.

Dependencies/integration: depends on local Git, fixture integrity, and SHA constants from fixture histories.

Risks/test signals: the third test name has a typo (`Unoved`) but behavior is clear. Coverage is narrow to tags and does not directly test branch refs or update-ref transaction failures.
