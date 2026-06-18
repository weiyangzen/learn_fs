# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/2

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/2`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: ptrace set regs (&{R15:NUM R14:NUM R13:NUM R12:NUM Rbp:ADDR Rbx:ADDR R11:NUM R10:NUM R9:NUM R8:NUM Rax:NUM Rcx:AD`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: ptrace set regs (&{R15:NUM R14:NUM R13:NUM R12:NUM Rbp:ADDR Rbx:ADDR R11:NUM R10:NUM R9:NUM R8:NUM Rax:NUM Rcx:AD, TYPE=DoS, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 52 lines and 3662 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 13 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.
- This fixture expects suppression; broadening or narrowing suppression regexes can change whether syzkaller reports the crash.

## Test Signals
- Primary signal: expected title `panic: ptrace set regs (&{R15:NUM R14:NUM R13:NUM R12:NUM Rbp:ADDR Rbx:ADDR R11:NUM R10:NUM R9:NUM R8:NUM Rax:NUM Rcx:AD`, expected type `DoS`, expected suppression.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: ptrace set regs (&{R15:NUM R14:NUM R13:NUM R12:NUM Rbp:ADDR Rbx:ADDR R11:NUM R10:NUM R9:NUM R8:NUM Rax:NUM Rcx:AD`.
- Expected report begins with: `panic: ptrace set regs (&{R15:512 R14:218 R13:219 R12:32 Rbp:139868397907264 Rbx:50432192 R11:646 R10:0 R9:0 R8:0 Rax:0 Rcx:4567363 Rdx:842350500544 Rsi:842350500848 Rdi:17 Orig_rax:202 Rip:4566688 Cs:51 Eflags:646 Rsp:8`.
