# sources/sync-backup/git-lfs/t/fixtures/migrate.sh

## Purpose
Shared fixture library for Git LFS migration tests. It constructs many small repositories with controlled commit graphs, ref layouts, attributes, remotes, tags, symlinks, dirty working trees, special filenames, and corrupted LFS tracking states so migration commands can be tested against known histories.

## Important APIs, Functions, and Control Flow
The file exposes setup helpers such as `setup_local_branch_with_gitattrs`, `setup_local_branch_with_nested_gitattrs`, `setup_single_local_branch_untracked`, `setup_single_local_branch_tracked`, `setup_single_local_branch_tracked_corrupt`, `setup_multiple_local_branches`, `setup_multiple_remote_branches`, tag variants, remotes variants, deep tree variants, symlink and dirty-copy variants, and `setup_local_branch_with_special_character_files`. `assert_ref_unmoved` validates refs after a migration operation. `make_bare`, `remove_and_create_local_repo`, and `remove_and_create_remote_repo` are lower-level constructors.

## State, Persistence, and Dependencies
Each setup function mutates the current test directory by creating a new repository, changing into it, committing generated files, optionally pushing to the test Git server, and configuring Git LFS attributes. It depends on `testlib.sh` helpers, `lfstest-genrandom`, `git lfs track`, `setup_remote_repo`, `clone_repo`, `add_symlink`, and environment flags such as `IS_WINDOWS`.

## Integration Points, Risks, and Test Signals
The fixture's outputs are consumed by migration test scripts, not run as standalone assertions. Its most important integration contract is the named repository topology described in comments and embodied by Git refs. Risks include hidden `cd` side effects, randomized repository suffixes, platform-specific symlink and filename support, and attribute precedence involving `.gitattributes`, `.git/info/attributes`, and global Git attributes. Good test signals are commit graph shape, expected file sizes, ref immobility, and whether corrupt tracked files remain non-LFS objects until migration repair.
