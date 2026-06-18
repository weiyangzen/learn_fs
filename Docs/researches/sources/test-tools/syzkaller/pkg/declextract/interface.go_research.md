# sources/test-tools/syzkaller/pkg/declextract/interface.go

Purpose: `interface.go` tracks discovered kernel interfaces and computes reachability, coverage, and access metadata for reporting or prioritization.

Important APIs/types/functions: `Interface` records type, name, identifying constant, source files, implementation function, access class, description availability, reachable LOC, and block coverage. `TristateVal` models unknown/yes/no flags. Interface kinds include syscall, netlink, fileop, ioctl, and io_uring. Access classes include unknown, user, namespace admin, and admin. `noteInterface`, `finishInterfaces`, `processFunctions`, `calculateLOC`, `collectLOC`, `findFunc`, `mustFindFunc`, `fileNameSuffix`, and `Tristate` are the key routines.

Control flow and state: `processFunctions` indexes functions by file-qualified and global names, merges coverage blocks into function scopes, links call graph edges, and counts callers. `finishInterfaces` sorts and deduplicates interfaces, disambiguates duplicate names with file suffixes, computes LOC/coverage, normalizes file lists, and fills default access. `collectLOC` recursively follows relevant scope calls while skipping very common callees.

Dependencies and integration: coverage comes from `pkg/cover`; function/scope facts come from `entity.go`; command-scope relevance uses `inferArgFlow` from `typing.go`. Interface records are created by syscalls, fileops, netlink, and io_uring passes.

Risks: duplicate access defaulting appears twice but is benign. LOC calculation depends on scope accuracy and ignores functions above a caller threshold, so results are prioritization signals rather than exact complexity. Missing functions produce warnings except for `mustFindFunc` callers.
