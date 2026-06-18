# sources/storage-engines/wiredtiger/tools/wt_cmp_dir

Purpose: compares logical content of two WiredTiger home directories by listing comparable URIs and delegating per-URI comparison to `wt_cmp_uri.py`.

Important APIs and control flow: `usage_exit()` prints arguments. `init_wt_utility()` walks upward from the current directory to find an executable `wt`. `wtfiles()` runs `$wt -h <home> list`, filters metadata URIs to include `table:*` and orphan `file:*` entries without matching tables, and emits one URI per line. CLI parsing supports a shared `-t timestamp`, an ignore regex `-i`, and an optional second `-t` for the second directory. It compares filtered URI lists exactly, then loops through each URI and runs `python3 <scriptdir>/wt_cmp_uri.py` with timestamp options and directory/URI paths, accumulating nonzero status.

State and persistence behavior: creates temporary `/tmp/wcd$$out` and `/tmp/wcd$$err` files during `wt list` and removes them. It reads WT homes and writes comparison progress to stdout/stderr.

Dependencies and integration points: requires a built `wt` utility in an ancestor directory, `wt_cmp_uri.py` next to the script, Python 3, grep/sed/tr, and usable WiredTiger home directories. It integrates with timestamped comparison workflows through `wt_cmp_uri.py`.

Risks: URI list equality is string-order sensitive. Temporary filenames based only on PID can collide in unusual circumstances. Paths like `"$dir1"/$f` assume URI strings are accepted by `wt_cmp_uri.py` in that form. The TODO notes corruption handling is not checked during list. Ignore regex is applied to URI lines and can hide relevant differences.

Test signals: successful comparison exits zero after printing each URI. Different URI lists produce an explicit stop message; per-URI differences produce nonzero final exit.
