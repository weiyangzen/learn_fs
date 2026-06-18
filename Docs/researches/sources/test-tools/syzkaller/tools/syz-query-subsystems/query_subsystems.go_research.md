# sources/test-tools/syzkaller/tools/syz-query-subsystems/query_subsystems.go

## Purpose
`syz-query-subsystems` queries Linux subsystem definitions from a kernel repository and saves them as a generated syzkaller subsystem list in another syzkaller checkout.

## Important APIs, types, and functions
- Flags specify OS, kernel repo, syzkaller repo, list name, optional subsystem filter, email/list inclusion, and debug output.
- `main` validates inputs, calls `linux.ListFromRepo`, optionally prints debug info, post-processes the list, creates `pkg/subsystem/lists`, gets kernel HEAD commit metadata, generates code, and writes `<name>.go`.
- `printDebugInfo`, `postProcessList`, `prepareFilter`, and `determineCommitInfo` support debug, filtering, email stripping, and VCS metadata.

## Control flow
Only Linux is accepted. Repository paths and generated list names are validated before expensive querying. Filtering is exact by subsystem `Name`, then `-emails=false` clears maintainer/list fields from every item. Commit info is fetched with `vcs.NewRepo(... OptPrecious, OptDontSandbox)` and `repo.Commit(vcs.HEAD)`.

## State and persistence behavior
Reads kernel and syzkaller repositories. Writes one generated Go file under the target syzkaller repository. Does not alter the kernel repository beyond VCS inspection; `OptPrecious` and `OptDontSandbox` indicate careful direct repo handling.

## Dependencies and integration points
Depends on `pkg/subsystem/linux` for Linux extraction, `pkg/subsystem` filtering, `pkg/vcs` for commit metadata, and the local generator in `generator.go`. Integrates with syzkaller's `pkg/subsystem/lists` registry.

## Risks and edge cases
The exact-name filter does not trim subsystem names from the data side. Invalid regex strings in skip logic do not apply here, but invalid list names fail early. Current implementation supports only Linux; other OS values are hard failures. Generated output can fail if generator creates duplicate identifiers.

## Test signals
No direct tests. Useful coverage includes validation failures, filter behavior, email stripping, debug printing, and generated file path/content checks against a small fake repo abstraction.
