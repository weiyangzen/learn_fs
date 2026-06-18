# sources/sync-backup/bup/test/int/test_treesplit.py

Purpose: regression/integration coverage for split-tree naming and depth decisions when bup stores directories with many entries under `bup.split.trees=1`.

Important APIs/types/functions: `tree._abbreviate_tree_names`, `split_tree_for_filenames()`, `pruned_ls_files()`, `diff_split()`, `git.init_repo`, `mkdirp`, bup CLI `index` and `save`, and Git `ls-tree -r --name-only`.

Control flow: `test_abbreviate()` checks shortest unique abbreviations for ordinary names, `.bupm`, strange names, and a single entry. Large fixtures `split_src`, `split_1`, and `split_2` encode deterministic source filenames and expected split-tree layouts. `split_tree_for_filenames()` initializes a repo, enables split trees, creates files, indexes and saves them, lists the saved Git tree, then prunes paths and collapsed `.bupm` internals. Depth-1 and depth-2 tests compare actual layout to expected fixtures with unified diff output.

State and persistence behavior: creates a temporary bup repository, writes many files, sets Git config `bup.split.trees`, saves into Git objects, and reads resulting tree names. The test's persistent state is the exact split directory structure using `..1.bupd` and `..2.bupd` names plus `.bupm` metadata placement.

Dependencies/integration points: bridges bup tree-splitting logic, metadata tree entries, Git storage, command execution helpers, and filesystem filename ordering. `pruned_ls_files()` intentionally normalizes Git output to focus on the saved source subtree.

Risks and test signals: fixture lists are large and brittle but provide strong regression coverage for deterministic split boundaries. Failures produce a unified diff of expected versus actual split layout, making off-by-one depth or abbreviation changes visible.
