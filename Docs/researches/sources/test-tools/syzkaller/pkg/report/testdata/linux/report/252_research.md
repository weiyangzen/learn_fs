<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/252 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/252

## Purpose
This negative fixture verifies that a standard perf NMI latency message is ignored. The log says `INFO: NMI handler (perf_event_nmi_handler) took too long to run: 2.277 msecs` and has no expected title.

## Important APIs, Types, and Functions
The key interfaces are the blank-header `ParseTest` contract and Linux suppression regexes for `INFO: NMI handler` and long-running handlers. `perf_event_nmi_handler` is data text, not a kernel crash frame to title.

## Control Flow
`parseReport` stores the INFO line as raw log. The Linux reporter scans it, matches suppression/noise logic, and should return nil so the expected empty `ParseTest` compares equal.

## State and Persistence Behavior
The fixture is immutable raw text with no expected metadata and no runtime state.

## Dependencies and Integration Points
It integrates with the Linux report parser's benign-info filtering and the generic test harness nil-report handling.

## Risks and Edge Cases
If the parser treats every `INFO:` line as a report, this file would produce a false positive. If suppression is too broad, adjacent real INFO reports such as RCU stalls must still parse, so this fixture constrains the benign subset.

## Test Signals
The only acceptable output is no report: empty title, empty alternatives, unknown type, and all flags false.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/252 -->
