# sources/test-tools/strace/maint/update_copyright_years.sh

Purpose: updates copyright year spans for git-tracked files based on commit history and optionally stages/commits the changes.

Important APIs/types/functions: environment defaults `COPYRIGHT_NOTICE`, `COPYRIGHT_MARKER`, `COPYRIGHT_PREFIX`, `VERBOSE`, `CALL_GIT_ADD`, `CALL_GIT_COMMIT`; functions `log`, `debug`, `print_help`, `get_comment_prefix`, and `process_file`; options `-v`, `-q`, `-a`, `-c`, `-j`, `-h`; parallel background job control.

Control flow: parse options, enumerate `git ls-files` excluding imported paths, process files in parallel up to `MAX_JOBS`. For each file, detect comment prefix, find current copyright years, derive first/last commit years with `git log`, skip up-to-date files, update existing notice or call the awk helper to add a notice, optionally `git add`, then optionally commit after all jobs finish.

State and persistence behavior: edits files in place, creates/removes temporary `.out` files, can stage and commit. Uses Git history as the source of truth for year spans.

Dependencies and integration points: maintenance script for repository headers; integrates with `update_copyright_years.awk` and Git.

Risks: concurrent background edits are safe per file but output ordering is nondeterministic. Existing notice regex may miss nonstandard forms. `COPYTIGHT_PREFIX` is misspelled in help, while variable is `COPYRIGHT_PREFIX`.

Test signals: dry runs on selected files should update only stale notices; `git diff` should show expected year-span changes and no touched ignored imported files.
