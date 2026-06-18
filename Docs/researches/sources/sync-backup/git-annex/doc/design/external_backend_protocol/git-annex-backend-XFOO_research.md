<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/design/external_backend_protocol/git-annex-backend-XFOO -->
# sources/sync-backup/git-annex/doc/design/external_backend_protocol/git-annex-backend-XFOO

Purpose: executable demonstration of the external backend protocol for generating and verifying git-annex keys. It implements a toy `XFOO` backend using MD5 and file size.

Important functions and protocol messages: `hashfile` runs `md5sum` and extracts the digest. The main loop responds to `GETVERSION` with `VERSION 1`, `CANVERIFY` with yes, `ISSTABLE` with yes, and `ISCRYPTOGRAPHICALLYSECURE` with no. `GENKEY contentfile` emits `GENKEY-SUCCESS XFOO-s<size>--<md5>` or failure. `VERIFYKEYCONTENT key contentfile` recomputes the MD5 and compares it to the suffix after `--`.

Control flow: the script reads line-oriented requests from stdin, splits with `set -- $line`, switches on the first word, and writes one protocol response to stdout. Unknown requests emit `ERROR protocol error`.

State and persistence: stateless; all derived state comes from the requested content file and key string.

Dependencies and integration points: POSIX shell, `md5sum`, `wc`, `cut`, and `sed`. It must be installed in `PATH` as `git-annex-backend-XFOO` for git-annex to discover the backend.

Risks: MD5 is explicitly non-cryptographic and the script says so. Shell word splitting makes paths with whitespace unsafe. Verification only compares the hash suffix, not the embedded size. `set -e` can terminate the backend on unexpected command failures.

Test signals: protocol tests should send each command, verify exact response tokens, use files with known MD5/size, check invalid keys, and include filenames with spaces to document limitations.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/design/external_backend_protocol/git-annex-backend-XFOO -->
