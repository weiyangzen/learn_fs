<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config.hpp -->
# sources/user-network-fs/mergerfs/src/config.hpp

## Purpose

This mergerfs source file is part of the support layer around configuration, filesystem operations, or FUSE integration. The source was read as a complete 224-line file (6279 bytes).

## Important APIs, Types, and Functions

types: `Config`, `CfgConfigFile`, `Err` functions: `to_string`, `from_string`, `finish_initializing`, `has_key`, `keys_listxattr`, `keys_listxattr_size`, `get`, `set`, `from_stream`, `from_file`, `is_rootdir`, `is_ctrl_file`, `is_mergerfs_xattr`, `is_cmd_xattr`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The global `cfg` persists process-wide mount configuration. Config-file errors accumulate in `errs`; `_initialized` freezes read-only options; config xattr listings are generated from `_map`; nested config includes are bounded by thread-local depth.

## Dependencies and Integration Points

direct includes: `branches.hpp`, `category.hpp`, `config_cachefiles.hpp`, `config_debug.hpp`, `config_dummy.hpp`, `config_flushonclose.hpp`, `config_follow_symlinks.hpp`, `config_inodecalc.hpp`, `config_link_exdev.hpp`, `config_log_file.hpp`, `config_moveonenospc.hpp`, `config_nfsopenhack.hpp`, `config_noforget.hpp`, `config_pagesize.hpp`, and 25 more

## Risks and Edge Cases

Wrong defaults or map entries can change mount semantics globally. Read-only enforcement must remain correct after initialization, config-file recursion must stay bounded, and xattr list sizing must match the bytes actually written.

## Test Signals

Unit tests for defaults, key aliases, unknown/read-only options, config-file parsing errors, recursion depth, xattr list sizing/content, and runtime set/get round trips.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config.hpp -->
