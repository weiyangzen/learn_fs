<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/makefiles/makefiles.go -->
# sources/user-network-fs/rclone/cmd/test/makefiles/makefiles.go

Source read: complete file, 310 lines, 9099 bytes, sha256 `ff975e608d1fabfc728350812cbed7b85f85ff33987b2e12914dd5ce526cef0e`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/makefiles/makefiles.go_research.md`.

## Purpose
Implements developer commands for generating random file trees or fixed-size files for testing.

## Important APIs, types, and functions
`makefilesCmd`, `makefileCmd`, shared flags, `commonInit`, `makefiles`, readers (`zeroReader`, `asciiReader`, `chargenReader`), `fileName`, `dir.createDirectories`, `dir.list`, and `writeFile` are the main functions.

## Control flow
`makefiles` mode builds a random directory tree according to file count, average files per directory, max depth, sizes, and seed, then writes files with selected content source. `makefile` mode parses one size and writes each named file. Common init chooses deterministic/random seed and validates mutually exclusive content flags.

## State and persistence behavior
Persistent state is the generated local filesystem files and directories. Global package variables hold flags, random source, content reader, directory counts, and used filenames for the current command run.

## Dependencies and integration points
Depends on the rclone test command group, fs size suffix flags, file mkdir helpers, random string helpers, pattern readers, and os/filepath IO.

## Risks and edge cases
Global filename uniqueness is process-wide for one run and does not reset between command invocations in the same process. Sparse files rely on filesystem support. Random tree shape can vary widely with parameters; seed controls reproducibility.

## Test signals
Manual test-data generation utility; no unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/makefiles/makefiles.go -->
