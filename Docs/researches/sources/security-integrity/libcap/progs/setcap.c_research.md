# sources/security-integrity/libcap/progs/setcap.c

Purpose: command-line tool to set, remove, or verify file capabilities.

Important APIs/functions: `pos_uint()` parses namespace root IDs. `read_caps()` reads cap text from stdin. `main()` handles `--license`, `-f`, `-h`, `-n`, `-q`, `-v`, `-r`, `-`, and repeated cap/file pairs. It uses `cap_from_text()`, `cap_set_nsowner()`, `cap_set_file()`, `cap_get_file()`, `cap_compare()`, and `cap_get_nsowner()`.

Control flow: before writing, it raises effective `CAP_SETFCAP` once from the process capability set. Verification compares both capability vectors and rootid. Linux-specific validation rejects effective file capabilities that are not empty or equal to permitted/inheritable union unless `-f` is used.

State and dependencies: mutates filesystem security xattrs and process effective caps. Depends on libcap, kernel file cap support, and regular files.

Risks and test signals: empty whitespace is rejected to avoid accidental clears; symlink removal is expected to fail in `quicktest.sh`. Namespace rootid support is validated by `quicktest.sh`.
