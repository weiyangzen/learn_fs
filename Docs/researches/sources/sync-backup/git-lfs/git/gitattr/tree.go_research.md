# sources/sync-backup/git-lfs/git/gitattr/tree.go

Purpose: builds an in-memory tree of `.gitattributes` blobs from a Git tree and answers which attributes apply to a path, including optional system, user, and repo-info attributes.

Important APIs/types/functions: `Environment`, `Tree`, `New`, `NewFromReader`, `FindSpecialAttributes`, `linesInTree`, `Applied`, and internal `applied`.

Control flow: `New` creates a shared `MacroProcessor`, parses the current tree's `.gitattributes` blob if present, recursively descends into subtrees, and keeps only children containing attributes. `FindSpecialAttributes` loads system, user, and repo-info attribute files into sibling `Tree` nodes. `Applied` lazily processes macros, then applies system, user, in-tree, and repo-info attributes in order; recursive `applied` matches current-level patterns and descends by the first path component.

State/persistence behavior: reads Git objects and optional filesystem config files. It caches parsed child trees and macro state in memory; no writes occur.

Dependencies/integration: uses `gitobj.ObjectDatabase`, `gitattr.ParseLines`, `MacroProcessor`, and attribute path resolver functions from `files.go`. `lfs/gitscanner_tree.go` separately uses `AttrPathsFromReader` for tree scans, but this file provides the richer tree application model.

Risks/test signals: symlinked `.gitattributes` is rejected as an error. Macro processing is lazy and shared, so call order matters if tree instances are mutated. Tests cover root/subtree application, discovery, macro use, pruning irrelevant child trees, and special-attribute precedence.
