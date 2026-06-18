# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc3.c

## Purpose
Implements miscellaneous LanguageLevel 3 operators: clip save/restore and procedure equality testing.

## Key Functions
- `zclipsave()` and `zcliprestore()` wrap graphics-state clipping save/restore.
- `zeqproc()` compares two procedures recursively to depth 10.

## Important Behavior
- `.eqproc` requires array/procedure operands and descends only when both nested arrays have equal sizes.
- Executable attributes intentionally do not need to match, matching Adobe behavior used for idiom recognition.
- Names and strings are not considered equal even if their object comparison would otherwise pass.

## Research Notes
Small LL3 support file used by clipping and `bind` idiom recognition behavior.
