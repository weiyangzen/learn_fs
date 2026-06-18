<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-cover/syz-cover.go -->
# sources/test-tools/syzkaller/tools/syz-cover/syz-cover.go

## Purpose

Coverage report generator from raw PCs or coverage history file view.

## Important APIs, Types, and Functions

Flags config/modules/exports/period/date/file/repo/commit/namespace/debug/force; functions `toolFileCover`, `initModules`, `doReport`, `readPCs`, `loadModules`.

## Control Flow

File mode renders historical file coverage; normal mode loads manager config/modules, builds report generator, reads PCs or all callback points, runs selected exports, writes outputs, and starts xdg-open.

## State and Persistence Behavior

Writes HTML/CSV/raw/JSON report files; reads rawcover and module JSON.

## Dependencies and Integration Points

Depends on manager config, kernel obj/src, coverage backend/db, xdg-open for interactive use.

## Risks and Edge Cases

Opening outputs is bad for headless CI; malformed PC aborts; `all` omits JSON/JSONL.

## Test Signals

Test PC parsing, each export, modules override, file mode with mocked DB.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-cover/syz-cover.go -->
