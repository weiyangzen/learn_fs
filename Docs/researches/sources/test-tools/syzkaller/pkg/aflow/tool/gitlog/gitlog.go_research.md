# sources/test-tools/syzkaller/pkg/aflow/tool/gitlog/gitlog.go

## Purpose
Exposes bounded git history, show, and blame operations as aflow tools for Linux kernel research.

## Important APIs, Types, and Functions
Exports `ToolLog`, `ToolShow`, `ToolBlame`, and `Tools`. `gitLog` supports code-regexp, symbol `-L`, message regexps, path history, count limiting, and no-merge behavior. `gitShow` validates commits and optional file presence. `gitBlame` clamps line ranges. `gitBadCallError`, `truncate`, and `runGit` normalize errors/output.

## Control Flow
Each tool runs inside `kernel.UseLinuxRepo`. `gitLog` builds arguments from mutually constrained search modes and caps count at 100. `gitShow` checks commit existence with `cat-file` and optional path presence with `ls-tree` before `git show`. `gitBlame` bounds ranges to `maxOutputLines`.

## State and Persistence Behavior
Read-only over the Linux git repository. It temporarily switches/uses the repo through the kernel action helper but stores no durable state.

## Dependencies and Integration Points
Depends on `aflow`, `kernel.UseLinuxRepo`, `osutil`, and `vcs`. Integrated by codeexpert when git support is enabled.

## Risks and Test Signals
Risks are broad/time-consuming history searches, invalid regexes, missing commits, and excessive diff output. Tests cover show, blame, log search modes, no matches, bad arguments, missing files/commits, and bad regex handling.
