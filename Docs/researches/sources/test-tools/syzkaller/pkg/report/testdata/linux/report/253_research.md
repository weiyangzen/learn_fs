<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/253 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/253

## Purpose
This negative fixture covers corrupted/interleaved console text that resembles a perf NMI warning but is not a kernel crash. It has no headers and must parse as no report.

## Important APIs, Types, and Functions
The relevant parser pieces are blank-header fixture handling, Linux suppression patterns for NMI handler messages, and robustness against garbled printk text. The recognizable token is `perf_event_nmi_handler`; the rest of the line is intentionally scrambled.

## Control Flow
The harness reads the garbled line as raw log with no expected title. The reporter must not manufacture a crash title from malformed `INFO:` content, and it must tolerate the unusual spacing and mixed fragments without corruption failures.

## State and Persistence Behavior
The file persists one raw noise line. It has no stateful behavior.

## Dependencies and Integration Points
It depends on syzkaller's Linux noise filtering and on scanner/test harness behavior for files with an initial blank line.

## Risks and Edge Cases
Too-strict text matching could stop suppressing this noisy line, while too-broad matching could hide real garbled kernel crashes. This fixture specifically guards the perf-NMI noise path.

## Test Signals
The expected parse is empty: no title, type, panic, corruption, or report body.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/253 -->
