<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/Connectathon_config_parsing.h -->
# sources/user-network-fs/nfs-ganesha/src/include/Connectathon_config_parsing.h

## Purpose
`Connectathon_config_parsing.h` declares configuration structures and parser helpers for Connectathon-style test parameters. It is separate from the main Ganesha runtime config and describes test directories, log files, and per-test workload settings.

## Important APIs, types, and functions
- `enum test_number` names test cases `ONE` through `NINE`.
- `struct btest` stores per-basic-test parameters: test numbers, levels, file/dir counts, sizes, block size, path/name strings, and linked-list pointer.
- `struct testparam` stores top-level `dirtest`, `logfile`, and linked `btest` list.
- Lifecycle helpers include `btest_init_defaults()`, `testparam_init_defaults()`, and `free_testparam()`.
- Accessors include `get_test_directory()`, `get_log_file()`, and `get_btest_args()`.
- `readin_config()` reads a config file into a `struct testparam`.

## Control flow
Implementation code initializes defaults, parses a config file into linked `btest` nodes, and returns a `testparam` object. Consumers query the top-level directory/log path and retrieve arguments for a specific numbered test.

## State and persistence
The header defines heap-backed config objects with owned strings and linked nodes. Persistence is external in the config file read by `readin_config()`. `free_testparam()` is responsible for releasing parsed in-memory state.

## Dependencies and integration points
It has no included dependencies beyond C language types. It likely integrates with Connectathon test support code rather than core server runtime.

## Risks
- The include guard name `_CONFIG_PARSING_H` is generic and can collide with the main config parsing header guard.
- Ownership rules for returned strings and `btest` nodes are not documented in the header; misuse can leak or double-free.
- Parser error behavior is not visible from the prototype; callers need implementation knowledge for malformed files.
- SPDX license is marked unknown, which may need cleanup for compliance tooling.

## Test signals
- Parser tests should cover missing fields, defaults, all test numbers, linked-list ordering, and cleanup.
- Include collision tests should build code that includes this header with main config headers.
- Sanitizer runs should verify `free_testparam()` releases all strings and nodes from `readin_config()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/Connectathon_config_parsing.h -->
