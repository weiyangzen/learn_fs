# sources/sync-backup/rsync/help-from-md.awk

## Purpose

`help-from-md.awk` generates a C help header from a fenced Markdown section. The caller passes `-v hfile=help-NAME.h NAME.NUM.md`; the script finds a Markdown comment that references the output header and converts the following code fence into `rprintf(F, "...\\n");` lines.

## Important APIs, Types, And Functions

The script uses AWK `BEGIN`, pattern actions, and `END`. Key variables are `hfile`, `ARGV[1]`, `heading`, `findcomment`, `backtick_cnt`, `prints`, and `foundcomment`. It uses `sub()` to escape a literal dot in `hfile`, `gsub()` to escape double quotes in help text, and writes generated output with redirection to `hfile`.

## Control Flow

At startup the script constructs a generated-file heading and a regex matching `[comment]` followed by the requested header name. Every line beginning with triple backticks increments `backtick_cnt` and is not copied. Once the comment is found, lines inside the first fenced block are escaped and appended to `prints`. Encountering a second fence exits the scan. In `END`, if the section was found and closed, the script writes the heading plus accumulated `rprintf()` statements. Otherwise it prints a failure message and exits 1.

## State, Dependencies, And Integration

The script persists only the generated header file. It is part of the build-time documentation/help pipeline and expects Markdown source conventions to remain stable: a comment marker naming the header followed by a fenced block containing literal help text.

## Risks

The regex only escapes the first dot in `hfile`, so unusual header names with multiple regex metacharacters could match more broadly than intended. Only double quotes are escaped; backslashes in help text are not doubled, so C escape sequences in Markdown can be interpreted by the generated C compiler. It assumes the wanted help text is in the first code fence after the marker and treats more than one opening fence as completion.

## Test Signals

Tests should generate a known help header from Markdown, verify quotes are escaped, verify missing comment and unterminated fence fail, check multiple help sections, and compile a generated header containing backslashes, percent signs, and empty lines.
