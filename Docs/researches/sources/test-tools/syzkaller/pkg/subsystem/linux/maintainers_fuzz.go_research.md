# sources/test-tools/syzkaller/pkg/subsystem/linux/maintainers_fuzz.go

## Purpose

`maintainers_fuzz.go` exposes the Linux MAINTAINERS parser to Go fuzzing or syzkaller's dead-code-aware fuzz harness. Its goal is robustness: arbitrary bytes should not crash the parser even when they produce parse errors internally.

## Important APIs, Types, and Functions

`Fuzz(data []byte) int` wraps `parseLinuxMaintainers(bytes.NewReader(data))` and ignores the returned records and error. `init` calls `runtime.KeepAlive(Fuzz)` to mark the function as used for dead-code checking.

## Control Flow

The fuzz entry converts input bytes into an `io.Reader`, invokes the parser, discards the result, and always returns `0`. Panics, scanner issues, regexp compilation paths, comment-state transitions, and email parsing edge cases are therefore surfaced as fuzz failures rather than handled outcomes.

## State, Dependencies, Risks, and Test Signals

There is no persistent state. Dependencies are `bytes`, `runtime`, and the parser in `maintainers.go`. The useful integration point is automated fuzz infrastructure that discovers parser panics or pathological inputs. Because the harness ignores errors, it tests crash-safety rather than parse correctness. It also does not seed structured MAINTAINERS inputs by itself, so coverage quality depends on the external fuzz corpus.
