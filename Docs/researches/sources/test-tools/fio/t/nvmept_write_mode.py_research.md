# sources/test-tools/fio/t/nvmept_write_mode.py

Purpose: destructive NVMe passthrough write-mode coverage for fio `io_uring_cmd`, including pure `write`, `verify`, `zeroes`, `uncor`, mixed percentage parsing, and verification behavior after write-zeroes or write-uncorrectable commands.

Important APIs and types: `WriteModeTest` builds common fio arguments and validates JSON data directions. `WriteModeSplit` parses `write_mode` percentage syntax, reads fio debug output, maps selected NVMe opcodes (`write`, `write_uncor`, `write_zeroes`, `verify`) to counters, and checks distribution within 10 percent. `WriteModeVerify` extends that by counting debug verification messages for uncorrectable and zeroes paths.

Control flow: `main()` parses `--dut`, creates artifacts, resolves fio from the build tree by default, injects filename, and runs `TEST_LIST`. The test matrix preconditions the device, checks verify-only workloads, writes zeroes and validates zero reads, creates uncorrectable ranges and expects subsequent reads/verifies to fail, then exercises valid and invalid mixed-mode expressions. Verification tests require `--debug=io,verify` so the checker can infer opcode and verify activity.

State and persistence: the target device is modified by writes, write zeroes, and write uncorrectable operations. The script persists fio output files and parses those files after execution. Test ordering is meaningful because preconditioning tests feed later verification tests.

Dependencies and integration points: depends on fio write-mode support, NVMe passthrough via `io_uring_cmd`, fiotestlib, and `SUCCESS_NONZERO`. It is registered in `run-fio-tests.py` as an NVMe character-device executable test.

Risks and test signals: debug-output parsing is sensitive to fio message text such as `op selected`, `errored io_u`, and `verifying write zeroes`. Mixed-mode expected counts use integer rounding, so small total IO counts would be noisy; the configured 16M filesize provides enough samples. Success signals include correct fio exit status, JSON direction activity, opcode mix distribution, expected parser failures for bad `write_mode`, and matching counts for special writes and their verify handling.
