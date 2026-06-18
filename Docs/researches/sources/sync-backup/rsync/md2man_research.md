# sources/sync-backup/rsync/md2man

## Purpose
`md2man` is a compatibility entry point for rsync's markdown-to-manpage converter. In this source tree it is a symlink to `md-convert`, so invoking `md2man` executes the same Python 3 converter implementation.

## Important APIs, Types, and Functions
The source path itself contributes no independent code beyond the symlink target. Its effective API is the `md-convert` command-line interface: `--test`, `--dest`, `--force-link-text`, `--debug`, and one or more markdown input files.

## Control Flow
At filesystem resolution time, `md2man` resolves to `md-convert`. Runtime behavior then follows `md-convert`: parse arguments, choose a markdown parser, convert each file to HTML and optional nroff, validate links, and write generated outputs.

## State and Persistence
`md2man` stores no independent state. Persistence effects are the same as `md-convert`: generated `.html` files and optional manpage files in the current or destination directory.

## Dependencies and Integration Points
The symlink preserves an older or clearer tool name for build scripts or developer workflows that expect `md2man`. It integrates with the same Python dependencies and rsync documentation inputs as `md-convert`.

## Risks
The key risk is symlink portability in packaging or archive extraction. If a platform or packaging step dereferences, omits, or breaks the symlink, callers using `md2man` fail even though `md-convert` exists. Behavioral changes must be documented against `md-convert` because this path has no separate implementation.

## Test Signals
Validation should include `ls -l` or equivalent packaging checks confirming the symlink target, invocation through `./md2man --test ...`, and build rules that call either name. Content correctness should be tested through the shared `md-convert` behavior.
