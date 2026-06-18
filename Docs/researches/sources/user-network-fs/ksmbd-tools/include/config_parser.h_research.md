<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/config_parser.h -->
# sources/user-network-fs/ksmbd-tools/include/config_parser.h

## Purpose

Public interface for parsing ksmbd configuration, password database, subauth, and lock files.

## Important APIs, Types, and Functions

Defines `struct smbconf_group`, global `struct smbconf_parser parser`, inline helpers `cp_printable`, `cp_smbconf_eol`, `cp_pwddb_eol`, parser lifecycle functions, file parsers, key/value conversion helpers, list parsing/freeing, and `cp_group_kv_steal`.

## Control Flow

Runtime code initializes parser state, parses `ksmbd.conf` and `ksmbdpwd.db`, transforms string values into booleans, numbers, config options, and lists, then destroys state through remove_config or parser-specific cleanup.

## State and Persistence Behavior

Parser state is global and mutable: hash-table groups plus current/global/ipc pointers. It also reads lock/subauth files and exposes derived configuration to management modules.

## Dependencies and Integration Points

Used by all CLIs, mountd startup/reload, addshare/adduser mutation paths, and tools load/remove helpers.

## Risks and Edge Cases

Global parser state makes reentrancy and reload ordering important. Key comparison is case/space normalized in implementation, so callers should use helper APIs rather than raw hash behavior.

## Test Signals

Tests should parse comments, duplicate groups/keys, empty values, list separators, numeric suffixes, invalid lock files, and load/remove cycles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/config_parser.h -->
