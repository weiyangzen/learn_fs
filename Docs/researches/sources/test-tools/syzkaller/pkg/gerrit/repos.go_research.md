# sources/test-tools/syzkaller/pkg/gerrit/repos.go

## Purpose
`repos.go` defines the whitelist mapping from Linux kernel repository clone URLs to Linux Gerrit project names accepted by `CreateChange`.

## Important APIs, Types, And Functions
`projectForRepo(repo)` returns the Gerrit project string or an unsupported-repository error. The package-level `projects` map is initialized by a function that enumerates supported kernel.org repository suffixes and emits URL variants for `git://git.kernel.org`, `https://git.kernel.org`, and `https://kernel.googlesource.com`.

## Control Flow
At package initialization, `kernelOrgRepos` is iterated. For every repo suffix, `project` is set to `linux/kernel/git/<repo>`, and three canonical clone URL forms are inserted into the map. `projectForRepo` performs an exact string lookup and returns an error if the lookup yields the zero string.

## State And Persistence Behavior
The only state is immutable in-process package data after init. There is no persistence, network access, or dynamic discovery of Gerrit projects.

## Dependencies And Integration Points
The file imports only `fmt`. It is consumed by `gerrit.go` before change creation. The supported set encodes syzkaller policy about which kernel.org repositories are mirrored in Linux Gerrit.

## Risks And Edge Cases
The lookup is exact and does not normalize trailing slashes, missing `.git`, SSH URLs, or alternate mirrors. Unsupported but valid kernel.org repos are rejected intentionally. Adding a repository requires code change and test updates. A repo with an empty project string would be indistinguishable from missing, though this initializer never creates such entries.

## Test Signals
`repos_test.go` verifies three accepted URL forms and one unsupported valid repo. Additional tests could cover every suffix, missing `.git`, and future URL forms if support expands.
