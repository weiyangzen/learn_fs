# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_conf.py

## Purpose

`ganesha_conf.py` is a command-line editor for `/etc/ganesha/ganesha.conf` or a file named by `CONFFILE`. It applies block/key operations using `Ganesha.config_editor.BLOCK`.

## Important APIs, Types, and Functions

`modify_file(filename, data)` writes replacement data atomically through a same-directory temporary file and preserves existing ownership/mode when possible. `get_blocks(args)` separates block descriptors from `--key value` or `--key` options. Top-level command handling supports `set`, `get`, and `del`.

## Control Flow

The script parses the opcode, extracts block names and key/value lists, constructs a `BLOCK`, reads the config file, then calls `set_keys`, `get_keys`, or `del_keys`. `get` exits with the retrieved value. `set` and `del` atomically replace the config file with modified text.

## State and Persistence Behavior

This script is a persistent file mutator. It writes to `/etc/ganesha/ganesha.conf` by default and uses `CONFFILE` for testing or generated conversions. Atomic rename protects against partial writes, and fsync is called on the temporary file.

## Dependencies and Integration Points

It depends on `Ganesha.config_editor`, `os`, `sys`, and standard file APIs. `knfs2ganesha-exports.py` drives it as an external command to build generated export configs.

## Risks and Edge Cases

`NamedTemporaryFile` opens in binary mode by default, but `modify_file` writes `str` data, which raises `TypeError` in Python 3 unless the data is bytes or the file is opened in text mode. It uses broad exception handling around stat/chown/chmod. It does not lock the target config file, so concurrent invocations can race. The parser limitations and `has_key` issue in `config_editor.py` affect this script.

## Test Signals

Tests should run with `CONFFILE` pointing to a temp file, cover set/get/del, verify atomic replacement preserves mode, and run under Python 3 to catch text/binary write behavior.
