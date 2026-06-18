# sources/security-integrity/selinux/scripts/run-flake8
# sources/security-integrity/selinux/scripts/run-flake8

Purpose: repository helper for running flake8 with a project-specific ignore list.

Important APIs and control flow: if no args are given, finds Python files and Python shebang scripts outside `.git`, then builds a long `IGNORE_LIST` of currently tolerated warnings/errors and execs `flake8 --max-line-length=120 --builtins='_,basestring,unicode'`.

State and persistence: no file writes; exits with flake8 status.

Dependencies and integration points: used by CI/developers; depends on find, grep, sort, flake8, and shell.

Risks and test signals: the ignore list is intentionally broad, so flake8 is a weak style gate until warnings are removed. It is itself a test signal for Python syntax/lint regressions.
