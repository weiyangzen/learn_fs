# sources/security-integrity/libcap/progs/getcap.c

Purpose: command-line tool to display file capability xattrs.

Important APIs/functions: option parser supports `-r`, `-v`, `-n`, `-h`, and `-l`. `do_getcap()` is used directly or via `nftw()` to inspect regular files with `cap_get_file()`, render via `cap_to_text()`, and optionally print namespace root owner via `cap_get_nsowner()`.

Control flow: each argument is `lstat()`ed. Recursive mode walks physical files; non-recursive mode maps stat type to an FTW-like flag. Missing caps are silent except under verbose mode.

State and dependencies: global flags hold verbosity, recursion, and namespace display. Depends on libcap and filesystem traversal.

Risks and test signals: symlink and non-regular files are deliberately not treated as targets. Recursive traversal errors are reported but do not stop the full scan. `quicktest.sh` validates namespace file-cap display with `getcap -n`.
