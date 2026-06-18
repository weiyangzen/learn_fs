# sources/test-tools/syzkaller/pkg/aflow/tool/grepper/grepper.go

## Purpose
Provides a bounded `git grep` aflow tool for broad textual searches in kernel sources.

## Important APIs, Types, and Functions
`Tool` registers `grepper`. `state` carries `KernelSrc`; `args` carries an extended regexp and optional path prefix; `results` returns formatted output. The implementation invokes `git grep --extended-regexp --line-number --show-function -C1`.

## Control Flow
The tool builds git args, runs under a one-hour timeout, converts no-match and bad-expression cases into `BadCallError`, then truncates long lines to 200 characters and long outputs to 500 lines with a header.

## State and Persistence Behavior
Read-only over the git checkout. No cache or persisted state.

## Dependencies and Integration Points
Depends on `aflow` and `osutil.RunCmd`. Used by codeexpert and agents when precise codesearch is insufficient.

## Risks and Test Signals
Risks include expensive regexes, binary/very long lines, and huge match sets. Tests cover normal output, long-line truncation, output truncation, no matches, bad regex, path prefix filtering, and expressions beginning with dash.
