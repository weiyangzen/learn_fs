# sources/test-tools/crashmonkey/ace/cmAdapter.py

## Purpose

`cmAdapter.py` converts ACE J-lang workload descriptions into CrashMonkey-style C++ test files. It starts from a base C++ test skeleton, finds insertion points for `setup`, `run`, `check_test`, and private declarations, then inserts generated C++ snippets for each J-lang command. The generated file becomes a runnable CrashMonkey test that executes filesystem operations through `cm_` wrapper methods and returns checkpoint-specific values.

## Important APIs, Types, and Functions

The CLI is defined by `build_parser()`, accepting `--base_file`, `--test_file`, `--target_path`, and `--output_name`. `create_dir()` ensures the target directory exists. `create_dict()` returns a small operation count map, but it is only initialized in `main()` and not otherwise used.

Insertion offset management is done by `updateSetupMap()`, `updateRunMap()`, `updateCheckMap()`, and `updateDefineMap()`. These functions keep later section indices aligned after lines are inserted into earlier C++ sections.

`insertDeclare()` adds integer declarations near the run section. `insertDefine()` declares and initializes path variables in setup, run, check, and private sections. It maps J-lang logical names to C++ identifier fragments by removing slashes, and maps the special `test` name to `mnt_dir_`.

Operation-specific code emitters include `insertFalloc()`, `insertMkdir()`, `insertOpenFile()`, `insertMknodFile()`, `insertOpenDir()`, `insertRemoveFile()`, `insertTruncateFile()`, `insertClose()`, `insertRmdir()`, `insertFsync()`, `insertSync()`, `insertLink()`, `insertCheckpoint()`, `insertRename()`, `insertFsetxattr()`, `insertRemovexattr()`, and `insertWrite()`. `insertWrite()` handles three materially different write modes: normal `WriteData`, `mmapwrite` through CrashMonkey mmap/msync wrappers, and direct `pwrite` after reopening with `O_DIRECT|O_SYNC`.

`insertFunctions()` is the dispatch function. It reads a J-lang command line, chooses the correct emitter, updates insertion indices, and writes the modified C++ file back. `main()` wires the parser, skeleton copying, insertion-point discovery, J-lang region parsing, and final file generation.

## Control Flow

`main()` validates that the J-lang test file exists, creates the target directory, derives a local `base_file` path inside the target, and reads that base file to discover the line indices of `setup()`, `run(`, `check_test(`, and `private:`. It then copies the base file to a new output path derived from `test_file + ".cpp"` under the target directory.

The J-lang file is processed line by line. Blank lines are skipped. Lines beginning with `#` switch the active destination method, using the last token as the region name. In `define` and `declare` sections, `insertDefine()` and `insertDeclare()` run directly. In `setup` and `run`, `insertFunctions()` dispatches the operation-specific insertion routine.

Each insertion routine reads the current generated C++ file into memory, inserts a formatted C++ snippet at the tracked index for the active method, updates all affected indices, seeks back to the beginning, and rewrites the file. For operations with checkpoints, `insertCheckpoint()` inserts `cm_->CmCheckpoint()`, increments `local_checkpoint`, compares it against the runtime `checkpoint`, and returns the J-lang-provided value when the target checkpoint is reached.

## State and Persistence Behavior

The adapter persists exactly one generated C++ file per invocation, plus any existing copied base file in the target directory. Its principal mutable state is `index_map`, a dictionary of insertion offsets, and the module-level `redeclare_map`, which suppresses repeated `int fd_*`, `filep_*`, and write buffer declarations. `redeclare_map` is never reset inside `main()`, which is harmless for one-process one-file CLI invocations but unsafe if this module is reused in-process for multiple files.

The file uses repeated read-modify-write cycles for every inserted J-lang line. This is simple but expensive for large workloads and exposes partially rewritten output if the process fails mid-generation. There is no atomic temp-file replacement.

## Dependencies and Integration Points

The adapter depends on the base C++ skeleton having recognizable function signatures and a `private:` section in the expected textual format. Generated snippets assume CrashMonkey helpers such as `cm_->CmOpen`, `cm_->CmClose`, `cm_->CmFsync`, `cm_->CmFdatasync`, `cm_->CmSync`, `cm_->CmCheckpoint`, `cm_->CmRename`, `cm_->CmMmap`, `cm_->CmMsync`, and `cm_->CmMunmap`, plus helper functions or system calls such as `WriteData`, `fallocate`, `mkdir`, `mknod`, `remove`, `unlink`, `rmdir`, `truncate`, `link`, `symlink`, `fsetxattr`, `removexattr`, `posix_memalign`, `memcpy`, and `pwrite`.

The upstream integration point is ACE J-lang syntax. Commands emitted by `ace.py` or the legacy sequence generators are consumed verbatim by splitting on spaces. That makes spacing, token order, and option formatting part of the interface.

## Risks and Test Signals

Parsing is fragile because it relies on `line.split(' ')` and exact token positions. Multiple spaces, tabs, or C++ skeleton signature changes can break insertion-point discovery or command parsing. Path-derived C++ identifiers are formed by concatenating path components, so name collisions are possible for different logical names that reduce to the same slashless string.

The base file copy behavior is easy to misread: the code computes `base_file` under `target_path`, but the `copyfile(base_test, base_file)` call is commented out. This means the target base skeleton must already exist before adapter execution, which `ace.py` satisfies by copying `base.cpp` once before invoking the adapter. Running `cmAdapter.py` directly with only `--base_file` may fail if the corresponding basename is absent in `--target_path`.

Generated direct-write and mmap snippets allocate or map resources but do not always free allocated direct I/O buffers, and error paths may close invalid descriptors. `insertMknodFile()` stores the return value of `mknod()` in an `fd_*` variable even though `mknod()` returns status, not an open descriptor. These may be intentional enough for generated tests but are risk points for runtime correctness.

Good validation signals include feeding minimal J-lang files for each supported command, compiling the generated C++, checking checkpoint return behavior, and diffing generated snippets against expected fixtures. Adapter tests should include paths with directories, repeated writes to the same file to exercise `redeclare_map`, and skeletons with the expected section markers.
