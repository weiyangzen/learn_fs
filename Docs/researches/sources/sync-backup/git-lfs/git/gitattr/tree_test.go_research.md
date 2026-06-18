# sources/sync-backup/git-lfs/git/gitattr/tree_test.go

Purpose: tests attribute application and tree discovery over synthetic Git object databases.

Important APIs/types/functions: `Tree.Applied`, `New`, `gitobj.FromFilesystem`, `WriteBlob`, `WriteTree`, and manual `Tree` structures using `wildmatch`.

Control flow: early tests use a hand-built tree to assert root and subtree matching. Later tests write blobs and trees to a temp object database, construct `Tree` with `New`, and verify attributes apply through direct and indirect child trees. Additional tests cover macro expansion and ordering across system/user/tree/repo attribute trees.

State/persistence behavior: uses temporary object databases but no durable repo mutation. The tests validate that irrelevant subtrees are pruned from the in-memory `children` map.

Dependencies/integration: depends on `gitobj` and `testify`. It provides regression coverage for tree-recursive discovery and precedence-sensitive macro processing.

Risks/test signals: covers many in-memory cases but not actual system/user attribute path discovery from disk; those are mostly exercised indirectly elsewhere.
