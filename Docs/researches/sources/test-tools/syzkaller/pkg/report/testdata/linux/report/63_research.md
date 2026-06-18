# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/63

## Purpose
This is a third minimal corrupted RCU stall fixture.

## Important APIs, types, and functions
The raw signal is `INFO: rcu_sched self-detected stall on CPU`; the expected parser metadata supplies the title, alternate, hang type, and corruption flag.

## Control flow
The report contains no trustworthy stack. The parser should recognize the RCU stall class and stop at `corrupted` attribution.

## State and persistence behavior
`CORRUPTED: Y` is the key persisted state. The fixture intentionally preserves insufficient crash context.

## Dependencies and integration points
It provides another regression sample for minimal RCU stall handling.

## Risks and test signals
False frame extraction is the main risk. The correct result is the exact corrupted hang title.
