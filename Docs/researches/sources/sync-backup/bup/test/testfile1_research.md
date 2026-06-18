# sources/sync-backup/bup/test/testfile1

## Purpose

`sources/sync-backup/bup/test/testfile1` is an ASCII executable test fixture, not a normal importable module. Its text is ROT13-encoded Python, and the decoded content is a concatenation of bup command scripts. The full 5,580-line file consists of three byte-identical 1,860-line copies of the same decoded command corpus. This makes it useful as deterministic bulk input for tests that need realistic source-shaped data with many repeated tokens, shebangs, option specs, functions, classes, repository operations, and filesystem interactions.

The decoded corpus covers bup command entry points for directory recursion, splitting and saving data into git-style objects, repository indexing, VFS listing and FTP-style browsing, FUSE mounting, random data generation, intentional pack damage, multi-index creation, server/client object transfer, remote backup helpers, fsck/par2 validation, progress-line normalization, and pack hash margin analysis. Because the file is ROT13-encoded, tests that consume it as raw bytes should not accidentally execute or import these command bodies.

## Important APIs, Types, And Functions

The fixture embeds command scripts that consistently use `bup.options.Options` to define command-line interfaces through `optspec` strings, parse `sys.argv[1:]`, and call `o.fatal()` on invalid usage. Many command bodies import common helpers from `bup.helpers`, including logging, progress output, `parse_num`, `saved_errors`, `add_error`, `chunkyreader`, `linereader`, `Conn`, and signal handling helpers.

Important decoded command groups include:

- `bup drecurse`: calls `drecurse.recursive_dirlist(extra, opt.xdev)` and optionally profiles iteration or suppresses filename output.
- `bup split`: configures `hashsplit.max_pack_size`, `hashsplit.max_pack_objects`, and `hashsplit.fanout`; writes blobs, trees, commits, or named refs through `git.PackWriter` or `client.Client`; supports noop/copy and benchmark modes.
- `bup memtest`: creates `git.PackIdxList`, generates random candidate object IDs with `/dev/urandom` and `mmap`, and repeatedly calls `m.exists()` while reporting `/proc/self/status` memory fields.
- `bup ls` and `bup ftp`: use `vfs.RefList`, node resolution, node iteration, `open()`, symlink/directory mode detection, shell quoting helpers, readline completion, and file extraction helpers.
- `bup fuse`: defines `Stat(fuse.Stat)`, `cache_get(top, path)`, and `BupFs(fuse.Fuse)` methods for `getattr`, `readdir`, `readlink`, `open`, `release`, and `read`.
- `bup init`: initializes local repositories and optionally creates/checks a remote repository through `client.Client`.
- `bup midx`: defines `merge(idxlist, bits, table)` and `do_midx(outdir, outfilename, infilenames)` to merge `.idx` files into `.midx` files with a fanout table and atomic rename from `.tmp`.
- `bup damage`: defines `randblock(n)` and overwrites random or evenly distributed regions of files with random bytes.
- `bup server`: defines protocol handlers `init_dir`, `set_dir`, `list_indexes`, `send_index`, `receive_objects`, `read_ref`, `update_ref`, and `cat`, dispatching them through a command map over `Conn(sys.stdin, sys.stdout)`.
- `bup join`: reads refs or object IDs from arguments or stdin and streams object content via local `git.CatPipe().join` or remote `client.Client.cat`.
- `bup save`: builds trees and commits from the bup index, with helper functions `eatslash`, `_push`, `_pop`, `progress_report`, `already_saved`, `wantrecurse_pre`, and `wantrecurse_during`.
- `bup tick`: sleeps until the next second boundary.
- `bup index`: defines `merge_indexes`, `IterHelper`, `check_index`, and `update_index`, updating or printing `git.repo('bupindex')` entries.
- `bup rbackup-server` and `bup rbackup`: implement reverse-server argument passing and an SSH bridge to a local `bup server`.
- `bup fsck`: wraps `git verify-pack`, optional quick pack SHA checks, and optional `par2` generate/verify/repair operations, including forked parallel jobs.
- `bup newliner`: rewrites carriage-return progress streams into stable newline output.
- `bup margin`: iterates `git.PackIdxList` and uses `_hashsplit.bitmatch()` to report the longest matching prefix between adjacent object IDs.

The only explicitly defined classes in the decoded fixture are `Stat`, `BupFs`, `IterHelper`, and `SigException`. There are no source-level definitions in the encoded fixture itself beyond the encoded text; all APIs become visible only after ROT13 decoding.

## Control Flow

The raw file control flow is just sequential text, but decoded analysis shows many independent command entry points separated by repeated `#!/usr/bin/env python` shebangs. If decoded and executed as one script, the first command body would run and later command bodies would also be parsed sequentially, but that is not the intended use. The shebang count and identical triplication indicate the file is a test input corpus rather than a runnable aggregate program.

Within each decoded command, control flow follows bup's command-line pattern: parse options, validate arity and incompatible modes, initialize repository/client state, run the command-specific work loop, report errors from `saved_errors` or return a nonzero status on failures. Long-running paths include:

- `split`, which chooses local, remote, noop, or copy writer behavior, streams input through hashsplit, writes trees/commits, closes the writer, then updates refs.
- `save`, which first optionally scans the index for progress totals, then iterates index entries, maintains a stack of path parts and tree shalists, validates or repacks index entries, writes file/symlink objects, pops pending trees, writes a final tree/commit, and updates refs.
- `index`, which merges a new writer over an old reader, marks deleted paths, updates stats and hashes, optionally verifies index invariants before and after update, and prints filtered status rows.
- `server`, which continuously reads line commands, dispatches handlers, sends framed binary payloads for indexes and object content, and supports a suspended pack writer during object receive.
- `fsck`, which normalizes pack-like filenames, chooses par2 or git verification, optionally repairs or generates recovery files, and can fork child processes to process multiple packs concurrently.

The second and third large segments repeat the first segment exactly, so there is no additional branch behavior in later copies.

## State And Persistence Behavior

The fixture itself is static test data with mode `0600` and no runtime state. Decoded command bodies, however, represent many persistent bup operations:

- Repository state is rooted through `git.repo(...)`, `git.init_repo()`, and `git.check_repo_or_die()`.
- Object persistence is handled by `git.PackWriter`, remote pack writers from `client.Client`, pack indexes, multi-index files, and git refs under `refs/heads/<name>`.
- `split` and `save` persist blobs, trees, commits, and named refs, and require pack writers to close before refs are updated.
- `index` persists bup index state in `git.repo('bupindex')`, including stat data, hash-valid flags, deletion markers, and repacked entries.
- `midx` writes `.midx.tmp` files, fills fanout tables, appends index names, then renames into the final `.midx` path.
- `server` can keep a global `suspended_w` pack writer across `receive-objects` protocol calls.
- `rbackup-server` mutates file descriptors and sets `BUP_SERVER_REVERSE` before `execvp`.
- `damage` deliberately mutates input files in place and is intentionally destructive.
- `fsck` may create `.par2` recovery files and may repair pack data when `--repair` is requested.

For tests using this file as input, the encoded state is intentionally inert unless a test decodes and executes it. The repeated corpus increases coverage for deduplication, splitting, compression, hashing, and indexing behavior because identical large regions should be detected by content-defined chunking or object reuse.

## Dependencies

Decoded dependencies are mostly internal bup modules: `options`, `drecurse`, `helpers`, `hashsplit`, `git`, `client`, `vfs`, `shquote`, `index`, `ssh`, `_hashsplit`, and likely the helper-provided `Sha1`, `Conn`, progress, logging, parsing, and terminal-state functions.

External and standard-library dependencies include `sys`, `os`, `stat`, `time`, `struct`, `mmap`, `math`, `glob`, `random`, `errno`, `tempfile`, `readline`, `fnmatch`, `re`, `subprocess`, `getopt`, `signal`, `fuse`, `/proc/self/status`, `/dev/urandom`, `/dev/null`, `git verify-pack`, `par2`, and SSH process plumbing through bup's `ssh` helper.

The raw fixture depends on none of these at read time. The notable dependency for understanding the file is ROT13 decoding.

## Integration Points

This file lives under `sources/sync-backup/bup/test/`, so its primary integration point is the bup test tree. Its shape is well suited for tests around:

- Hash-splitting and chunk boundary stability over realistic Python command text.
- Deduplication behavior, because the first 1,860-line decoded block is repeated exactly three times.
- Directory recursion or test-fixture scanning that must handle executable-looking files safely.
- Backup/save/index tests that need a nontrivial but deterministic payload.
- Encoding-handling tests, since meaningful Python appears only after ROT13.
- Tooling that detects shebangs, option specs, function/class definitions, and command names in source-like data.

The decoded command corpus integrates conceptually with bup's command wrappers and internal APIs, but the raw fixture should be treated as data. Any research or tests that infer behavior from it should account for the ROT13 transform and the triplication.

## Risks And Edge Cases

The largest risk is misclassification. A scanner that only checks for shebang-like bytes sees `#!/hfe/ova/rai clguba`, not a normal Python shebang, and a scanner that ROT13-decodes may see many runnable command scripts concatenated into one file. Treating the raw file as a valid script would be incorrect.

The file contains decoded examples of destructive or environment-sensitive command behavior, including `bup damage`, `fsck --repair`, FUSE mounting, SSH remote backup, repository ref updates, pack writes, and file descriptor manipulation. These are inert in the encoded fixture but risky if a test harness decodes and executes arbitrary sections.

The repeated content can skew metrics. Line counts, shebang counts, function counts, and API frequency are tripled relative to the unique corpus. Research and test assertions should distinguish unique behavior from repeated payload.

Several decoded command bodies are Python 2 style, using `print` statements, old exception syntax, octal literals like `040000`, and iterator `.next()`. This reinforces that the fixture represents historical bup source content and should not be assumed compatible with modern Python execution.

The fixture is large enough to exercise streaming code but small enough to avoid oversized-file chunking in research workflows. Consumers should still use streaming reads for backup/hash tests rather than loading by habit.

## Test Signals

Useful signals for validating consumers of this file:

- Raw size is 158,664 bytes and 5,580 lines.
- ROT13 decoding turns the first shebang into `#!/usr/bin/env python`.
- Raw shebang markers occur at 63 lines, corresponding to 21 command scripts repeated three times.
- Lines 1-1,860, 1,861-3,720, and 3,721-5,580 are byte-identical.
- The decoded unique segment includes command option specs for `drecurse`, `split`, `memtest`, `ls`, `ftp`, `random`, `help`, `fuse`, `init`, `midx`, `damage`, `server`, `join`, `save`, `tick`, `index`, `rbackup-server`, `fsck`, `rbackup`, `newliner`, and `margin`.
- The final decoded command prints the longest bit match from pack index iteration, while the final raw lines are the ROT13-encoded `margin` command body.

For repository tests, a good acceptance check is that reading the raw fixture remains side-effect-free, while ROT13-aware analysis can recover the command inventory and verify the three identical segments.
