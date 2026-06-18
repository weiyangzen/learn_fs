# sources/security-integrity/selinux/libselinux/fuzz/selabel_file_compiled-fuzzer.c

## Purpose
This libFuzzer harness exercises the compiled-file-contexts backend parser and lookup logic in libselinux. It feeds one to three compiled file-context data streams plus a lookup key into internal label-file routines and asserts core invariants on successful matches.

## Important APIs, types, and functions
The entry point is `LLVMFuzzerTestOneInput()`. Helpers include `null_log()`, `validate_context()`, `write_full()`, and `convert_data()`. The harness constructs a `struct selabel_handle`, `struct saved_data`, `struct spec_node`, and calls internal functions from `../src/label_file.h`: `load_mmap()`, `sort_specs()`, `cmp()`, `lookup_all()`, `free_lookup_result()`, and `free_spec_node()`. Control bits select partial matching, find-all mode, and whether to use `S_IFSOCK` mode.

## Control flow
The first input byte is a control byte. Remaining bytes are split on `0xde 0xad 0xbe 0xef` into required primary compiled data, optional homedir/local-style compiled data, and a lookup key. Each data segment is copied into memory, written to an anonymous memfd, converted to `FILE *`, and loaded with `load_mmap()` using file indexes 0, 1, and 2. The specs are sorted, self-comparison is asserted equal, `lookup_all()` is run, and each returned result is checked for nonempty regex/context, no translated context, validation, and prefix bounds.

## State and persistence behavior
All state is in process memory and anonymous memfds. The harness installs process-global SELinux callbacks for logging and validation. It manually cleans lookup results, spec tree data, mmap areas, key/data buffers, and FILE handles.

## Dependencies and integration points
It depends on libFuzzer, Linux `memfd_create`, `mmap`/`munmap`, libselinux public `label.h`, and private label-file internals. It is intended to be built in a fuzzing configuration that exposes internal parser functions.

## Risks and edge cases
Assertions are intentional fuzz oracles, so builds must run with assertions enabled for full checking. `memmem()` and `memfd_create()` are GNU/Linux-specific. The callback installation is global and could interfere if combined with other fuzz targets in one process. The harness copies fuzz slices before memfd writing, increasing memory pressure for large inputs.

## Test signals
Seed corpora should include valid compiled file-contexts data, malformed headers, multiple overlay files, empty and nonempty lookup keys, mode-sensitive patterns, partial matches, all-match queries, digest-related data, and separator-edge cases.
