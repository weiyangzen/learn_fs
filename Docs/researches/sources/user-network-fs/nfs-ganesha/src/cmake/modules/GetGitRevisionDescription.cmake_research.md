# sources/user-network-fs/nfs-ganesha/src/cmake/modules/GetGitRevisionDescription.cmake

## Purpose

`GetGitRevisionDescription.cmake` provides configure-time functions for deriving Git revision metadata while forcing CMake to reconfigure when `.git/HEAD` or the referenced branch file changes.

## Important APIs, Types, and Functions

Public functions are `get_git_head_revision(<refspecvar> <hashvar>)`, `git_describe(<var> [args...])`, and `git_get_exact_tag(<var> [args...])`. Internal state includes `_gitdescmoddir`, `GIT_DATA`, generated `grabRef.cmake`, `HEAD_REF`, and `HEAD_HASH`.

## Control Flow

The module guards against multiple inclusion, captures its own directory at include time, and uses `GANESHA_TOP_CMAKE_DIR` as the starting point for `.git` search. `get_git_head_revision` walks upward to find `.git`, copies `.git/HEAD` into `CMakeFiles/git-data`, configures the `.in` helper, includes it, and returns the ref and hash. `git_describe` finds Git, obtains the hash, runs `git describe <hash> ...` in the top source tree, and stores a `-NOTFOUND`-style string on failure. `git_get_exact_tag` calls `git_describe --exact-match`.

## State and Persistence Behavior

The module writes generated files under `${CMAKE_CURRENT_BINARY_DIR}/CMakeFiles/git-data` so CMake tracks Git ref files as configure inputs. Returned revision variables are caller-scoped through `PARENT_SCOPE`.

## Dependencies and Integration Points

It depends on Git, CMake `configure_file`, and the companion `GetGitRevisionDescription.cmake.in`. It feeds version strings such as package release metadata, including RPM release values using `_GIT_HEAD_COMMIT_ABBREV`.

## Risks and Edge Cases

It assumes `GANESHA_TOP_CMAKE_DIR` is set. Worktrees or `.git` files that point elsewhere may not be handled because the code expects `.git/HEAD` under a directory. The TODO command-injection check is commented out, although `execute_process` argument lists reduce shell injection risk. Shallow or tagless clones can yield `-NOTFOUND` descriptions.

## Test Signals

Configure in normal branch, detached HEAD, tag, shallow clone, and non-Git source archive states. Verify CMake re-runs after committing or changing branch refs and that package version variables update.
