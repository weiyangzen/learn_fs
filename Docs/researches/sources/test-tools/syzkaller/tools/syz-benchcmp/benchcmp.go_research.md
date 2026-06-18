<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-benchcmp/benchcmp.go -->
# sources/test-tools/syzkaller/tools/syz-benchcmp/benchcmp.go

## Purpose

Visualizer for syz-manager benchmark JSON streams.

## Important APIs, Types, and Functions

Types `Graph`, `Point`; functions `readFile`, `addExecSpeed`, `skipStart`, `restoreMissingPoints`, `printFinalStats`, `display`; Go HTML template with Google Visualization.

## Control Flow

Reads JSON records, derives exec speed, merges metrics by x-axis, filters graphs, sorts/skips/interpolates points, prints final stats, writes HTML, opens browser unless `--out`.

## State and Persistence Behavior

Writes temp/requested HTML; graph data in memory.

## Dependencies and Integration Points

Depends on JSON bench files, browser/xdg-open, Google JSAPI in generated HTML.

## Risks and Edge Cases

Zero means missing during interpolation, which can be wrong; default negative skip removes first 30 percent.

## Test Signals

Small multi-file bench fixtures for missing points, `--all`, `--out`, custom `--over`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-benchcmp/benchcmp.go -->
