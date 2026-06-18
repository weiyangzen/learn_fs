# sources/test-tools/crashmonkey/copy_diff.sh

Purpose: shell helper that classifies a CrashMonkey diff output as pass/fail/could-not-run, appends failing diffs to `diff_results/<target>`, optionally invokes detailed diff parsing, and cleans transient `build/diff*` files.

Important APIs/types/functions: positional args `_file`, `_target`, optional `_demo`, `tput` colors, file tests `-f`/`-s`, `cat`, `source find_diff.sh`, and `rm build/diff*`.

Control flow: validates input file, if non-empty prints failed, appends content, optionally parses it for demo output, and removes diffs. If empty, it checks whether diff files existed in `build`; if so, removes them and prints passed; otherwise prints could-not-run.

State/persistence behavior: mutates `diff_results`, deletes `build/diff*`, and may update bug counters through `find_diff.sh`. Dependencies/integration: called by `xfsMonkey.py` and demo workflows.

Risks/test signals: unquoted variables can break on spaces/globs, `rm build/diff*` can error when no files match, and sourcing `find_diff.sh` runs it in the caller shell with shared variables.
