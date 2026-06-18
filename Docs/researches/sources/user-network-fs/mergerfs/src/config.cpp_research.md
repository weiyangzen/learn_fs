<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config.cpp -->
# sources/user-network-fs/mergerfs/src/config.cpp

## Purpose

This is the runtime configuration registry for mergerfs. It owns the global `cfg`, constructs every mount/config option with defaults, maps user-visible option names to `ToFromString` adapters, parses config files and key-value writes, exposes config xattrs, and enforces read-only options after initialization. The source was read as a complete 525-line file (14775 bytes).

## Important APIs, Types, and Functions

types: `DepthGuard` functions: `Config::CfgConfigFile::CfgConfigFile`, `Config::CfgConfigFile::from_string`, `Config::CfgConfigFile::to_string`, `Config::Config`, `Config::has_key`, `Config::keys_listxattr_size`, `Config::keys_listxattr`, `Config::get`, `Config::set`, `Config::from_stream`, `Config::from_file`, `Config::finish_initializing`, `Config::is_rootdir`, `Config::is_ctrl_file`, and 5 more

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The global `cfg` persists process-wide mount configuration. Config-file errors accumulate in `errs`; `_initialized` freezes read-only options; config xattr listings are generated from `_map`; nested config includes are bounded by thread-local depth.

## Dependencies and Integration Points

direct includes: `config.hpp`, `errno.hpp`, `fmt/core.h`, `fs_path.hpp`, `nonstd/string.hpp`, `str.hpp`, `version.hpp`, `fstream`, `string`, `string.h`

## Risks and Edge Cases

Wrong defaults or map entries can change mount semantics globally. Read-only enforcement must remain correct after initialization, config-file recursion must stay bounded, and xattr list sizing must match the bytes actually written.

## Test Signals

Unit tests for defaults, key aliases, unknown/read-only options, config-file parsing errors, recursion depth, xattr list sizing/content, and runtime set/get round trips.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config.cpp -->
