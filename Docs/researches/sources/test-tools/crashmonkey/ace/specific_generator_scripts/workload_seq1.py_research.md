# sources/test-tools/crashmonkey/ace/specific_generator_scripts/workload_seq1.py

## Purpose

`workload_seq1.py` translates a j-lang workload skeleton into a CrashMonkey C++ test by inserting generated C++ snippets into a copied base test file. It is the first sequence translator variant and supports a wide set of filesystem operations including open, mkdir, fallocate, sync range, write, direct write, mmap write, link, rename, xattr operations, truncate, checkpoint, and sync.

## Important APIs, Types, and Functions

- CLI from `build_parser`: `--base_file`, `--test_file`, `--target_path`, and `--output_name`.
- `create_dir` ensures the target directory exists.
- `updateSetupMap`, `updateRunMap`, `updateCheckMap`, and `updateDefineMap` maintain insertion offsets as generated lines are inserted into the C++ file.
- `insertDefine` declares and initializes path strings in setup, run, check, and private sections.
- `insertDeclare` inserts integer local declarations in the run section.
- Operation emitters include `insertFalloc`, `insertSyncRange`, `insertMkdir`, `insertOpenFile`, `insertMknodFile`, `insertOpenDir`, `insertRemoveFile`, `insertTruncateFile`, `insertClose`, `insertFsync`, `insertSync`, `insertLink`, `insertCheckpoint`, `insertRename`, `insertFsetxattr`, `insertRemovexattr`, and `insertWrite`.
- `insertFunctions` dispatches j-lang lines to the proper emitter based on the first token and writes the modified C++ file back to disk.
- `main` discovers insertion points in the base C++ file, copies the base to a generated target, then processes the j-lang file section by section.

## Control Flow

The translator validates that the j-lang file exists, creates the target path, computes `base_file` as `target_path + basename(base_file)`, scans that base file for `setup()`, `run(`, `check_test(`, and `private:` insertion anchors, copies it to `target_path + test_file + "_" + output_name + ".cpp"`, and walks the j-lang file. Lines starting with `#` switch the active destination method (`define`, `declare`, `setup`, or `run`); other lines are inserted according to the active method.

## State and Persistence Behavior

The only durable product is the generated C++ test file. The translator edits this file repeatedly with read/insert/write cycles. `redeclare_map` is a global process-local guard to avoid duplicate declarations of generated variables such as file descriptors, mmap pointers, and direct-I/O buffers. `index_map` and `new_index_map` track evolving insertion offsets and are critical for keeping generated code in the intended C++ sections.

## Dependencies and Integration Points

The generated C++ depends on CrashMonkey `cm_` wrapper methods (`CmOpen`, `CmClose`, `CmFsync`, `CmFdatasync`, `CmSync`, `CmCheckpoint`, `CmMmap`, `CmMsync`, `CmMunmap`), helper functions such as `WriteData`, and symbols such as `TEST_FILE_PERMS`. It also emits direct Linux/POSIX calls like `mkdir`, `mknod`, `truncate`, `fallocate`, `link`, `symlink`, `rename`, `fsetxattr`, `removexattr`, `posix_memalign`, and `pwrite`. The output is meant to be built by the CrashMonkey Makefile as a shared test object.

## Risks and Edge Cases

- Python 2 only: uses `print` statements and `xrange`.
- `base_file` is resolved inside `target_path`, while the copy from the source base is commented out. A pre-existing base file must already be present in the target directory.
- File and variable names are made by removing slashes, so collisions are possible for different paths that flatten to the same string.
- The insertion-offset accounting uses hard-coded line counts for generated snippets; any snippet edits can corrupt subsequent insertion points.
- `insertMknodFile` treats `mknod` as returning a file descriptor, but POSIX `mknod` returns 0 on success, which can make generated close/error logic semantically wrong.
- Direct write uses plain `open` rather than `cm_->CmOpen`, unlike later variants, so it may bypass CrashMonkey instrumentation.
- Mmap write always `msync`s and unmaps 4096 bytes, regardless of the generated length, which can under-test larger mappings.

## Test Signals

Good signals are a generated `.cpp` file with populated setup/run/check/private sections, successful compilation through the CrashMonkey Makefile, and runtime execution where checkpoint return values stop at the intended crash points. Specific tests should cover `syncrange`, `mmapwrite`, `dwrite`, repeated variable use without redeclaration, and j-lang files containing all supported `#` sections.
