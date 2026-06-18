# sources/user-network-fs/samba/source3/script/fix_bool.pl

Purpose: Perl rewrite helper that replaces `True` with `true` and `False` with `false` in a target file.

Important APIs, types, and functions: opens input, writes `$ARGV[0].new`, applies regex substitutions once per line, then renames the temp file over the original.

Control flow: linear read-transform-write-rename.

State and persistence: modifies the target file in place via a sidecar `.new` file.

Dependencies and integration: requires Perl. It is a developer migration helper rather than runtime code.

Risks: substitutions are not global per line, are not token-aware, and can alter strings/comments or partial identifiers. Rename failure handling uses `die @_`, which is not the actual error variable.

Test signals: lines with multiple booleans, strings/comments, missing files, and rename failures.
