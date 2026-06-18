# Research: sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/4

## Purpose
This fixture is a gVisor `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/gvisor/report/4`. It validates that `gvisor.Parse` and `simpleLineParser` classify the supplied panic, fatal error, signal, data race, or suppression log as `panic: munmap(ADDR, NUM)) failed: invalid argument`.
The fixture is part of the generic `report/testdata/<os>/report` suite consumed by `TestParse`, so it verifies `ContainsCrash`, title replacement, suppression handling, report truncation, and `ParseFrom` boundaries.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `gvisor.Parse`, `gvisor.shortenReport`, `gvisorTitleReplacement`, `gvisorOopses`.
- Fixture metadata: TITLE=panic: munmap(ADDR, NUM)) failed: invalid argument, TYPE=DoS.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- gVisor-specific flow applies title replacements for container names, sandbox names, and PIDs, then truncates long Go goroutine dumps after the first useful panic/data-race stack block.

## State And Persistence
- Static fixture only: 98 lines and 8631 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- The embedded expected report block has 31 line(s), making report shortening and exact newline preservation part of the persistent golden contract.

## Dependencies And Integration Points
- Depends on `gvisorOopses`, `gvisorTitleReplacement`, suppression regexes from `ctorGvisor`, and the shared `report_test.go` parser harness. It integrates with `pkg/report` normalization rather than gVisor runtime code.

## Risks And Edge Cases
- gVisor panic output often includes long all-goroutine dumps; truncation must keep enough lines for the title while avoiding unstable goroutine noise.

## Test Signals
- Primary signal: expected title `panic: munmap(ADDR, NUM)) failed: invalid argument`, expected type `DoS`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: panic: munmap(ADDR, NUM)) failed: invalid argument`.
- Expected report begins with: `panic: munmap(2000d000, 0)) failed: invalid argument`.
