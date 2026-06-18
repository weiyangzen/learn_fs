# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/config_editor.py

## Purpose

`config_editor.py` implements a small parser and editor for NFS-Ganesha configuration blocks. It is used by `ganesha_conf.py` and `knfs2ganesha-exports.py` to set, get, and delete key/value pairs in nested config blocks.

## Important APIs, Types, and Functions

The pyparsing grammar defines `ppblock` as `BLOCKNAME { key=value;... subblocks... }`. `BLOCK` provides `set_keys`, `get_keys`, `del_keys`, and recursive helpers `set_process` and `del_process`. Utility functions include `r3_to_text`, validators for keys/values/block names, `next_subnames`, `block_match`, and `make_r3`. `ArgError` carries validation failures.

## Control Flow

Input text is scanned for blocks. A block descriptor such as `EXPORT Path /x CLIENT Clients *` is validated, then matched against parsed recursive three-element lists `[name, keypairs, subblocks]`. Setting finds or creates the target nested block and updates/appends key pairs. Getting formats all pairs or one requested key. Deleting removes requested keys, and can remove entire `EXPORT` or `CLIENT` blocks when identifying pairs are gone.

## State and Persistence Behavior

The parser/editor is pure over input strings and returns modified text. It does not write files directly. Formatting is regenerated for edited blocks using tab indentation, so comments and original formatting inside edited blocks are not preserved.

## Dependencies and Integration Points

It depends on `pyparsing`, `logging`, `pprint`, `re`, and `sys`. `ganesha_conf.py` handles file I/O and atomic replacement, while `knfs2ganesha-exports.py` shells out to `ganesha_conf` for generated export blocks.

## Risks and Edge Cases

The grammar requires all key/value pairs to precede sub-blocks, while comments note the daemon accepts more flexible ordering. Values cannot contain semicolons. `get_keys` uses `dict.has_key`, which is invalid in Python 3. Several paths call `sys.exit` inside library code, making composition and testing harder. Deletion checks `end_part[0]` without guarding empty suffixes. Reformatting edited blocks can drop comments and reorder whitespace.

## Test Signals

Parser tests should cover nested blocks, case-insensitive matching, `EXPORT`/`CLIENT` identifiers, set/get/delete of keys, whole-block removal, malformed keys/values, comments, and input where key pairs follow subblocks. Python 3 tests should specifically catch `has_key`.
