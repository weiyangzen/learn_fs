# sources/test-tools/lcov/scripts/getp4version

Purpose: older standalone Perforce version-script sample for lcov merge verification. It returns a P4 revision or fallback mtime/md5 signature for one filename.

Important APIs: modes are `getp4version [--md5] [--allow-missing] filename` and `getp4version --compare old_version new_version filename`. It supports special md5 comparison for non-P4 version strings.

Control flow and state: extraction canonicalizes the file, probes `p4 files` for repository membership, reads `p4 have` for a revision, checks `p4 opened` for local edits, appends mtime and optional md5 when needed, and prints the version string. Compare mode returns exact inequality except for md5 fallback strings where both sides have md5 tails.

Dependencies and integration: uses `annotateutil::get_modify_time` and `compute_md5`, plus external `p4`, `grep`, and shell redirection. It is a direct executable alternative to the module-oriented `P4version.pm`.

Risks and test signals: `p4 files $pathname` and other shell strings interpolate filenames without quoting. The script only handles edit local state in `p4 opened`, unlike `P4version.pm` which also considers add/delete/integrate. Test signals are P4 callback tests, missing file tests, local edit behavior, and md5 compare paths.
