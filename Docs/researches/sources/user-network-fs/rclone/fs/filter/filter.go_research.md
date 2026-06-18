<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/filter.go -->
# sources/user-network-fs/rclone/fs/filter/filter.go

## Purpose
Implements rclone's runtime file, directory, metadata, age, size, hash-partition, exclude-if-present, and files-from filtering.

## Important APIs, Types, And Control Flow
`OptionsInfo` defines global filter flags; `Options` stores parsed config. `NewFilter` copies options, computes age windows, parses hash filters, parses file and metadata rules, enforces files-from exclusivity, reads files-from lists, and optionally dumps filters. `Filter` tracks file/dir/meta rules, files-from maps, and hash partition parameters. Inclusion flow checks files-from first, then hash, path rules, directory rules, exclude marker files, age/size, and metadata rules. Context helpers manage global or context-local filters and a `use filter` marker. `MakeListR` converts files-from into a concurrent `ListR` callback producer.

## State And Persistence
Global `Opt` and `globalConfig` hold process-wide defaults. Individual filters store parsed maps and time windows. Rule files and stdin may be read; no filter state is written to disk.

## Dependencies And Integration Points
Integrates `fs.Options`, global options registration/reload, glob/rules parsing, metadata extraction, `fs.FileExists`, object listing callbacks, errgroup concurrency, and config context.

## Risks And Test Signals
Files-from overrides most other filters, hash filter uses normalized lower-case MD5 partitions, and metadata filtering treats absent metadata with a sentinel. Tests cover many construction and inclusion scenarios, docs examples, directory filters, metadata filters, and context config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/filter.go -->
