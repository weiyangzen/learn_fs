# sources/storage-engines/raft-engine/src/file_pipe_log/mod.rs

## Purpose
This module is the public assembly point for the filesystem-backed `PipeLog` implementation. It wires together the private format, file I/O, pipe, builder, and reader modules, then re-exports the crate-visible types that higher layers use to open raft-engine storage over log files. Its `debug` submodule provides public utility readers and writers for inspecting or rewriting physical log files outside the normal `Engine` path.

## Important APIs, Types, And Functions
The top-level exports map the implementation into stable names: `FilePipeLog` is `pipe::DualPipes`, `FilePipeLogBuilder` is `pipe_builder::DualPipesBuilder`, and recovery extension points include `ReplayMachine`, `RecoveryConfig`, and `DefaultMachineFactory`. It also re-exports filename helpers `FileNameExt` and `parse_reserved_file_name`.

`debug::build_file_writer` and `debug::build_file_reader` adapt a generic `FileSystem` to `LogFileWriter` and `LogFileReader`, opening files with the requested permission and passing the parsed or requested `LogFileFormat` to `log_file` helpers.

`debug::LogItemReader<F>` is an iterator over logical `LogItem`s. It supports `new_file_reader` for one physical log file and `new_directory_reader` for every file in a directory whose name parses as a `FileId`. Directory mode sorts by `FileId` so append and rewrite file sequence order is deterministic.

## Control Flow
`LogItemReader::next` drains a local `VecDeque<LogItem>`. When empty, it asks `LogItemBatchFileReader` for the next decoded batch. If the current file is exhausted, `find_next_readable_file` opens the next queued file, parses its header, and preloads the first non-empty batch. Decode or open errors reset the batch reader and surface as the iterator item error.

The iterator implementation delegates to the inherent `next` method. This intentionally lets callers use normal iterator syntax while preserving the custom error-yielding behavior.

## State And Persistence Behavior
The debug reader stores only transient state: the `Arc<FileSystem>`, remaining `(FileId, PathBuf)` queue, current reusable `LogItemBatchFileReader`, and decoded items awaiting delivery. It does not mutate source files. The writer utility can create or reopen files; with `create = true`, it force-resets through `build_file_writer`, which is used in tests to produce clean log files with the chosen format.

Because filename parsing uses `FileId::parse_file_name`, debug directory reads ignore unrelated files and subdirectories but will report corruption if a parsed log file is empty or malformed.

## Dependencies And Integration Points
This module depends on `env::FileSystem`, `log_batch::LogItem`, `pipe_log::FileId`, `LogFileReader`, `LogFileWriter`, and `LogItemBatchFileReader`. Production callers usually consume the re-exported `FilePipeLogBuilder`; diagnostic and scripting paths consume `debug::build_file_reader`, `debug::build_file_writer`, and `debug::LogItemReader`.

## Risks And Edge Cases
`new_file_reader` rejects non-files and filenames that do not parse as log files. `new_directory_reader` uses `std::fs::read_dir` rather than the configured `FileSystem`, so it is tied to local filesystem semantics even though actual file opens use `F`. A malformed file whose name looks valid causes iteration to return an error and then stop. Empty but well-formed files are accepted in single-file mode and skipped in directory iteration.

## Test Signals
`test_debug_file_basic` writes batches containing entries, commands, puts, and deletes across several files, then verifies both single-file and directory iteration reproduce drained `LogBatch` items. `test_debug_file_error` covers invalid file/directory arguments, unrelated files, corrupted files, and empty files. `test_recover_from_partial_write` verifies reopening a partially written or truncated file can replace the header format cleanly across V1/V2 combinations.
