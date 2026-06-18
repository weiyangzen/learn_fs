# sources/user-network-fs/samba/source3/script/mksyms.sh

Purpose: shell wrapper that runs `mksyms.awk` over header files and updates a symbol export file only when content changes.

Important APIs, types, and functions: sets `LANG`, `LC_ALL`, and `LC_COLLATE` to `C`; validates arguments; sorts and uniquifies header paths; runs awk to a temp file; uses `cmp -s`, `rm`, and `mv`.

Control flow: parse awk executable and output file, build sorted `proto_src`, generate temp output, compare with existing output, then either remove temp or replace the target.

State and persistence: writes or updates the requested symbol file and creates a temporary `.$$.tmp~` file during generation.

Dependencies and integration: depends on shell, awk, sort, uniq, cmp, and `mksyms.awk` in the same directory.

Risks: unquoted paths in `mkdir`, awk invocation, cmp, rm, and mv will break on spaces or shell metacharacters. Temp filename can collide if reused by stale processes.

Test signals: unchanged output path, changed output path, duplicate headers, missing awk, paths with spaces, and interrupted temp-file cleanup.
