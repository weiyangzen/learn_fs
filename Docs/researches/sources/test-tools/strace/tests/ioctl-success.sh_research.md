<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl-success.sh -->
# sources/test-tools/strace/tests/ioctl-success.sh

Purpose: `ioctl-success.sh` shell harness for ioctl decoder tests that need a successful ioctl via strace syscall injection. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are scno_tampering.sh, run_strace, match_diff, skip_, fail_, IOCTL_INJECT_START, IOCTL_INJECT_RETVAL, strace -e inject=ioctl:retval=...:when=... . Local include directives/macros observed in this source are `none in wrapper; inherited through included implementation` and `implementation defaults`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: sources the common shell helper, sanity-runs ../$NAME expecting failure or skip, reruns it under strace with ioctl injection starting at the configured call number, captures expected output from the test binary, filters noisy early fd ioctl lines from the strace log, then diffs. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl-success.sh` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: persists only temporary harness outputs $EXP and $OUT; behavior is driven by environment variables and the selected binary name. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: test harness variables NAME, LOG, EXP, OUT, srcdir; executable under ../$NAME must accept skip count and injected retval arguments. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: brittle if the binary cannot lock onto the injected call, if fd setup emits extra ioctl lines outside the filter, or if the configured injection start is stale. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Pass signal is match_diff equality between filtered strace output and the binary-generated expectation. This file has 31 source lines and 786 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl-success.sh_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl-success.sh -->
