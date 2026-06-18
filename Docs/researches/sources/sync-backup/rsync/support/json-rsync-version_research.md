<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/json-rsync-version -->
# sources/sync-backup/rsync/support/json-rsync-version

Purpose: normalize rsync `--version --version` output into JSON, including support for older rsync versions that do not emit native JSON.

Important APIs/types/functions: `main()`, `TWEAK_NAME` for renamed capability keys, `MOVE_OPTIM` for options that belong under optimizations, and argparse's optional `rsync` command argument.

Control flow: read version text from stdin when no rsync command is supplied, otherwise execute `[rsync, --version, --version]`; pass through native JSON unchanged; parse the version/protocol line, copyright, web site, list-style sections, and comma-style capability/optimization sections; coerce `no` to false and `N-bit` strings to integer bit counts; ensure standard keys exist; infer GPL version from major version; and dump JSON.

State and persistence behavior: no persistent state. It emits a single JSON object to stdout.

Dependencies and integration points: depends on Python 3, subprocess, json, and rsync version-output formatting. It supports tooling that wants structured rsync build capability metadata.

Risks: parser state depends on section headers and indentation. The variable `saw_comma` is initialized only after the first non-special section header, so unexpected indented lines before a header would fail. License inference is simplistic. Unknown formatting in future rsync versions can misclassify fields.

Test signals: feed native JSON, current text output, legacy text output, no-capability output, `no foo`, `64-bit`, and misplaced `asm/SIMD` optimizations; verify stable JSON keys and pass-through behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/json-rsync-version -->
