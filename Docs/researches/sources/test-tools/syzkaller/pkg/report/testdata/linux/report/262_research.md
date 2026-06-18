<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/262 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/262

## Purpose
This negative fixture ensures Android userspace/debug output and benign audio driver messages do not become Linux kernel crash reports. It has no expected headers and should parse as an empty report.

## Important APIs, Types, and Functions
The log contains `DEBUG:` backtrace lines for Android libraries such as `libart.so`, `libandroid_runtime.so`, `app_process64`, and `libc.so`, plus `audio_aio_open` and `audio_open` messages. Parser behavior under test is filtering of non-kernel userspace stack text.

## Control Flow
Because the file starts with a blank line, the harness records no expected metadata. The Linux reporter scans the userspace frames and audio messages and should return nil rather than treating function-like C++ symbols as kernel frames.

## State and Persistence Behavior
The fixture is immutable noise text with no expected title, type, or flags. It owns no state.

## Dependencies and Integration Points
It depends on Linux report parser boundaries, suppression/noise handling, and nil-report comparison in `report_test.go`.

## Risks and Edge Cases
The C++ symbols contain namespaces, shared-library paths, and offsets that can look like stack frames. A permissive parser could false-positive on them.

## Test Signals
The correct parse is empty: no title, no type, no report body, and all flags false.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/262 -->
