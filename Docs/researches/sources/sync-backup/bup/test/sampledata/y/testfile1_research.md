# sources/sync-backup/bup/test/sampledata/y/testfile1

## Purpose

`sources/sync-backup/bup/test/sampledata/y/testfile1` is an executable ASCII sample-data fixture in the bup test tree. The bytes are ROT13-encoded Python text, beginning with `#!/hfe/ova/rai clguba`, which decodes to `#!/usr/bin/env python`. Decoding the complete file reveals a concatenated corpus of historical bup command scripts repeated three times. The fixture is 158664 bytes and is used as stable, realistic file content for repository indexing, saving, metadata rewriting, object splitting, and size reconstruction tests.

This file should not be treated as an importable module in its checked-in form. Its primary contract is fixture stability: path, byte content, executable/text properties, and size are what downstream tests depend on.

## Important APIs, Types, and Functions Represented

The encoded corpus covers many bup command entry points and helper interactions:

- `bup drecurse`: uses `options.Options`, `drecurse.recursive_dirlist()`, profiler support, `saved_errors`, and helper logging.
- `bup split`: uses `hashsplit`, `git`, `client.Client`, `PackWriter`, pack size/object/fanout controls, `split_to_shalist()`, `hashsplit_iter()`, tree creation, commit creation, and ref updates.
- `bup memtest`: uses `git.PackIdxList`, `/proc/self/status`, `/dev/urandom`, and `mmap` to stress object existence checks.
- `bup ls` and `bup ftp`: use `vfs.RefList`, node traversal, node display helpers, readline completion, and file extraction.
- `bup random`: uses `_hashsplit` random generation and TTY-safety checks.
- `bup fuse`: defines `Stat(fuse.Stat)`, a path cache, and `BupFs(fuse.Fuse)` methods for `getattr`, `readdir`, `readlink`, and `open`.
- `bup init`, `midx`, `damage`, `server`, `join`, `save`, `tick`, `index`, `rbackup-server`, `fsck`, `rbackup`, `newliner`, and `margin`: collectively cover repository initialization, multi-index generation, deterministic file corruption, server protocol handlers, object reassembly, backup stack construction, index maintenance, remote backup plumbing, parity/checksum verification, signal handling, newline normalization, and pack hash-prefix margin checks.

Notable decoded functions/classes include `s_from_bytes()`, `report()`, `print_node()`, `node_name()`, `do_ls()`, `write_to_file()`, `inputiter()`, shell completer helpers, `Stat`, `cache_get()`, `BupFs`, `merge()`, `do_midx()`, `randblock()`, server command handlers such as `init_dir()`, `set_dir()`, `list_indexes()`, `send_index()`, `receive_objects()`, `read_ref()`, `update_ref()`, `cat()`, save-stack helpers such as `eatslash()`, `_push()`, `_pop()`, `progress_report()`, index helpers such as `merge_indexes()`, `IterHelper`, `check_index()`, `update_index()`, fsck helpers such as `par2_setup()`, `par2_generate()`, `par2_verify()`, `par2_repair()`, `quick_verify()`, `git_verify()`, `do_pack()`, and remote-backup signal handling via `SigException` and `handler()`.

## Control Flow

As stored, the file has no meaningful runtime control flow for bup itself because names and keywords are ROT13-obfuscated. If executed directly, it would be invalid for the expected Python/bup environment. For test fixture purposes, bup reads it as ordinary file bytes.

When decoded for analysis, the content is a sequence of standalone command scripts. Each script follows the old bup command pattern:

1. Declare an `optspec` block.
2. Parse `sys.argv[1:]` using `options.Options`.
3. Validate argument combinations and repository state.
4. Dispatch to bup library modules such as `git`, `hashsplit`, `index`, `drecurse`, `vfs`, `client`, or helper process wrappers.
5. Emit IDs, progress, listings, or status codes.
6. Update repository refs, pack indexes, metadata, or remote protocol state where appropriate.

The decoded corpus contains 63 shebang-marked script sections, corresponding to three repeated copies of the same command corpus. The repetition is part of the fixture bytes and contributes to its exact size and splitting behavior.

## State and Persistence Behavior

The fixture itself is static persistent test data. Its important state is the byte-for-byte content at `test/sampledata/y/testfile1`, including the ROT13 encoding, executable shebang-like first line, repeated script bodies, and 158664-byte length.

The decoded scripts describe stateful bup behaviors, including:

- Git-style object and pack persistence through `git.PackWriter`, `new_tree()`, `new_commit()`, `update_ref()`, `PackIdxList`, `.idx`, `.midx`, `.pack`, and optional `.par2` files.
- Backup naming under refs such as `refs/heads/<name>`.
- Index validity and fake validity/invalidity flags used by index/save tests.
- Remote persistence through `client.Client`, remote pack writers, and server command handlers.
- Filesystem presentation through `vfs.RefList` and FUSE path metadata.

In actual tests, bup persists this file as part of `test/sampledata`, then uses repository metadata and object content to recover or verify the file size. The fixture's own bytes should remain unchanged unless tests and expected metadata values are deliberately updated together.

## Dependencies

The fixture is consumed by bup tests as plain filesystem data. Tests depend on standard Unix file behavior, bup's index/save/get/ls commands, and repository storage under temporary `BUP_DIR` values.

The decoded script corpus references Python 2-era dependencies and bup internals:

- Standard modules: `sys`, `os`, `time`, `struct`, `re`, `stat`, `mmap`, `glob`, `random`, `math`, `errno`, `tempfile`, `readline`, `fnmatch`, `getopt`, `subprocess`, `signal`.
- External/platform interfaces: `/dev/urandom`, `/proc/self/status`, FUSE via `fuse`, SSH/remote subprocesses, `par2`, `git verify-pack`, and Unix process primitives such as `fork()` and `wait()`.
- bup modules: `options`, `helpers`, `drecurse`, `hashsplit`, `_hashsplit`, `git`, `client`, `vfs`, `shquote`, `index`, `ssh`.

Those decoded dependencies are not required to read the fixture, but they explain why the sample content is representative of bup's command surface.

## Integration Points

The file lives under `test/sampledata`, so it participates in whole-tree sample data saves and rewrites. The most direct observed integration is `sources/sync-backup/bup/test/ext/test-rewrite`, which:

- indexes `test/sampledata`;
- saves the sample tree multiple times;
- forces `test/sampledata/y/testfile1` to be re-saved with `bup index --fake-invalid`;
- verifies behavior when metadata encodes no size;
- checks that augmented listing can recover the real size `158664`;
- checks that `get --rewrite` writes metadata where later listing reports `158664` even without augmentation.

Other tests copy or save `test/sampledata` as a whole, so this file also contributes realistic payload bytes to fsck, import, metadata, tag, and miscellaneous save workflows.

## Risks and Maintenance Notes

- Size is part of the test contract. Changing any byte changes the expected 158664-byte size and can break rewrite/listing assertions.
- The content is intentionally obfuscated as ROT13 sample data. Replacing it with decoded Python or reformatting it would alter chunking, hashes, metadata, and test behavior.
- Executable-looking text may tempt maintainers to treat this as runnable source. It is safer to classify it as fixture data unless a test explicitly decodes it.
- The repeated corpus gives the file a large, structured, compressible payload. Deduplication and splitting behavior may depend on that structure.
- Python 2 syntax in the decoded text is historical fixture content, not necessarily live project code. Modernizing it inside this fixture would be a fixture mutation, not a code modernization.
- Any line-ending conversion, charset conversion, chmod changes, or sampledata regeneration should be checked against tests that assert file size, metadata, and object identity.

## Test Signals

Useful validation signals after changing related bup code are:

- `test/ext/test-rewrite`, especially the section that greps `save/latest/y/testfile1` for `-1122334455` and then `158664`.
- Whole sampledata save/index flows such as `bup index "$top/test/sampledata"` and `bup save -n save --strip "$top/test/sampledata"`.
- Metadata augmentation behavior in `bup ls -l save/latest/y/testfile1`.
- Rewrite behavior through `bup get --rewrite ... --append`.
- Low-level fixture checks: `wc -c test/sampledata/y/testfile1` should report `158664`, and decoding with ROT13 should still reveal the repeated bup command corpus.
