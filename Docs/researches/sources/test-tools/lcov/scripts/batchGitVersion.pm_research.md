# sources/test-tools/lcov/scripts/batchGitVersion.pm

Purpose: optimized git version-script callback that builds a repository-wide blob SHA database once, including submodules, and answers repeated `extract_version` calls from memory.

Important APIs: package `batchGitVersion` exports `new`, `extract_version`, `compare_version`, and `usage`. Options include `--md5`, `--allow-missing`, `--repo`, `--prepend`, repeated `--prefix`, `--token`, and verbose flags. Standalone execution delegates to `annotateutil::call_get_version`.

Control flow and state: `new` runs `git ls-tree -r --full-tree HEAD` in the main repo, records blob shas by path, tracks submodule commit entries, then runs `git submodule foreach` and stores submodule blob shas under composed paths. Prefixes are normalized with trailing slashes and used by `extract_version` to strip build-root path prefixes before hash lookup. Unknown existing files fall back to mtime plus optional md5.

Dependencies and integration: uses `annotateutil` for time/md5, `Getopt::Long`, `File::Spec`, and shell git commands. The returned version string is `"BLOB <sha>"` unless `--token` changes the token for backward compatibility.

Risks and test signals: the module explicitly does not detect local edits, so dirty working trees may compare equal. A regex for nested submodule commit lines appears narrow and may not match all `git ls-tree` formats. Shell command construction lacks quoting for repo paths. Tests should compare callback behavior against `gitversion.pm`, submodule fixtures, prefix/prepend behavior, and missing-file paths.
