<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/329 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/329

## Purpose
This fixture is a syzkaller Linux report-parser oracle for repeated page faults in `bpf_prog_kallsyms_find`. The expected metadata says the parser must report `BUG: unable to handle kernel paging request in bpf_prog_kallsyms_find`, classify it as `MEMORY_SAFETY_BUG`, keep the alternative `bad-access in bpf_prog_kallsyms_find`, and set both corrupted and panicked flags.

## Important APIs, Types, And Functions
The file is test data consumed by `pkg/report` test loading, not executable code. Its API surface is the header contract: `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, `PANICKED`, followed by the raw log. The kernel signature of interest is the x86 oops with `RIP: bpf_prog_kallsyms_find+0x289/0x4a0`, repeated many times with the same faulting address and empty `Call Trace:` sections.

## Control Flow
The parser reads the metadata block, then scans the console stream from the first `BUG: unable to handle kernel paging request`. The fixture stresses first-report selection and duplicate-oops handling: many nearly identical page-fault records follow, so `findFirstOops`, title extraction, and report trimming must not drift to later duplicates or panic epilogue text.

## State And Persistence
All state is persistent expected data in the fixture. The important persisted flags are `CORRUPTED: Y` and `PANICKED: Y`, reflecting a damaged report stream and eventual panic behavior. Dynamic addresses, CPUs, PIDs, and registers are intentionally present for normalizer coverage.

## Dependencies And Integration Points
This integrates with syzkaller's Linux oops regex catalog, bad-access title normalizer, BPF symbol handling, corruption detection, and crash type mapping. It is loaded by the report parser tests through the `report` testdata directory.

## Risks
The repeated same-site oopses can cause overlong or unstable selected reports if duplicate suppression changes. The empty call traces also mean the parser must rely primarily on the RIP symbol.

## Test Signals
The stable signal is title `BUG: unable to handle kernel paging request in bpf_prog_kallsyms_find`, type `MEMORY_SAFETY_BUG`, alt `bad-access in bpf_prog_kallsyms_find`, corrupted and panicked flags set, and a selected report anchored at the first `bpf_prog_kallsyms_find` RIP.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/329 -->
