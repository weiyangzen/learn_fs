# sources/storage-engines/foundationdb/contrib/apiversioner.py

Purpose: scans and optionally rewrites FoundationDB API version references across a source tree.

Important APIs/functions: constants `EXCLUDED_FILES`, `SUSPECT_PHRASES`; helpers `positive_response`, `rewrite_lines`, `address_file`, `address_path`, and `run`.

Control flow: CLI selects path, old version, optional new version, suspect-only mode, diffs, rewrite, confirmation, grayscale, and paths-only. Directory traversal skips generated/binary/third-party paths. In suspect mode it matches API-setting patterns; otherwise it finds standalone old-version numbers. Rewrites show contextual diffs and optionally prompt before changing lines.

State and persistence: read-only unless `--rewrite` is passed, in which case matched files are overwritten with joined rewritten lines.

Dependencies and integration: Python stdlib only. Intended for release/API maintenance.

Risks and test signals: broad non-suspect search can rewrite unrelated numbers; writing uses normal open without atomic replace; `matching_lines` filter truthiness is always true in Python 3, though iteration still controls logging. Test suspect regexes, excludes, diff-only, rewrite with/without confirmation, and UnicodeDecodeError handling.
