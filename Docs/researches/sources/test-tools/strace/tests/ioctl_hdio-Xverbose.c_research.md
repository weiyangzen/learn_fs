<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_hdio-Xverbose.c

Purpose: `ioctl_hdio-Xverbose.c` HDIO/IDE ioctl decoder test for drive settings, identity, command/task payloads, and xlat-backed flags. Wrapper chain: ioctl_hdio-Xverbose.c -> ioctl_hdio.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering.

Important APIs/types/functions: Primary APIs and data surfaces are HDIO_GET/SET_* commands, HDIO_DRIVE_CMD, HDIO_DRIVE_TASK, HDIO_DRIVE_TASKFILE, HDIO_GETGEO, HDIO_GET_IDENTITY, hd_driveid, hd_geometry, ide_task_request_t, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h. Local include directives/macros observed in this source are `ioctl_hdio.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection locks on HDIO_GET_QDMA; main covers scalar get/set commands, bus state and IDE nice xlat values, NULL and bad pointer cases, drive geometry, identity data, task/command byte arrays, and verbose/nonverbose payload presentation. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_hdio.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus tail-allocated hdreg objects and byte buffers. INJECT_RETVAL exposes output-side structures; VERBOSE expands larger HDIO buffers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/hdreg.h, xlat.h, xlat/hdio_busstates.h, xlat/hdio_ide_nice.h, ioctl-success.sh for success wrappers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: legacy IDE headers vary across platforms, xlat tables must match bundled values, and success-injected output must coordinate with the harness. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks known/unknown HDIO command names, scalar xlat values, pointer faults, structure/buffer truncation, and injected markers. This file has 3 source lines and 47 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_hdio-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_hdio-Xverbose.c -->
