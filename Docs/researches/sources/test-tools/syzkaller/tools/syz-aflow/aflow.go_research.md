<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-aflow/aflow.go -->
# sources/test-tools/syzkaller/tools/syz-aflow/aflow.go

## Purpose

CLI for registered syzkaller agentic workflows and syzbot bug input download.

## Important APIs, Types, and Functions

Flags workflow/input/workdir/model/cache/download/auth/html; functions `run`, `downloadBug`, `get`, `getAccessToken`, `parseSize`; uses `pkg/aflow` and trajectory HTML.

## Control Flow

Download mode queries syzbot and writes input JSON; run mode reads input, opens cache, executes selected flow, logs spans, and rewrites optional live HTML report.

## State and Persistence Behavior

Persists input JSON, workdir/cache artifacts, and optional HTML trajectory.

## Dependencies and Integration Points

Depends on registered flows, syzbot.org, optional Google ADC, filesystem workdir.

## Risks and Edge Cases

Direct JSON type assertions can panic on schema/no-crash changes; workflows may have broad side effects.

## Test Signals

Unit parse/download fixtures and a fake flow emitting spans/cache/HTML.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-aflow/aflow.go -->
