# sources/sync-backup/borg/src/borg/testsuite/archiver/completion_cmd_test.py

Purpose: tests generated shell completion scripts for Bash and Zsh, including size sanity, syntax validity, and Borg-specific Bash completion helper behavior.

Important APIs/types/functions: `cmd_available` detects shell availability. `needs_bash` and `needs_zsh` skip tests when shells are unavailable. `_run_bash_completion_fn` writes a generated completion script to a temp file, sources it in Bash, runs setup code, and captures output. `_check_shell_syntax` validates generated scripts with `shell -n`.

Control flow: nontriviality tests assert generated Bash/Zsh scripts are large enough and have many lines. Syntax tests run Bash/Zsh parsers. Bash helper tests simulate `COMP_WORDS`/`COMP_CWORD` for sort-key completion, files-cache mode mutual exclusions, archive name completion from a real repository, and `aid:` archive ID completion.

State and persistence behavior: temporary shell script files are created and unlinked. Archive completion tests create repositories and archives. Bash subprocesses source generated scripts and emit completion candidates without persisting shell state.

Dependencies and integration points: covers `borg completion bash/zsh`, generated preamble helper functions, repository archive listing used by completion, shell availability, and subprocess execution.

Risks: generated script size thresholds are coarse. Tests depend on internal Bash function names such as `_borg_complete_sortby`, `_borg_complete_filescachemode`, and `_borg_complete_archive`. Shell versions may differ in syntax handling.

Test signals: ensures completion output is not truncated, is syntactically valid for supported shells, and implements important dynamic completions and mutual-exclusion rules.
