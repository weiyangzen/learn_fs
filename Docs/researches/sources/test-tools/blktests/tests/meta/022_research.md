<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/022 -->
# sources/test-tools/blktests/tests/meta/022

Purpose: blktests harness self-tests that verify skip and failure handling around `requires()`, `device_requires()`, and device-array entry points. This specific test is declared as: "skip test_device_array() in device_requries()".

Important APIs/types/functions: sourced libraries `tests/meta/rc`; top-level variables `DESCRIPTION=skip test_device_array() in device_requries()`; functions `device_requires()` lines 11-13, `test_device_array()` lines 15-17; external commands `echo`.

Control flow: `device_requires()` is present and carries the file-specific action body. `test_device_array()` uses commands `echo`.

State and persistence behavior: records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `meta` suite and the shared harness; through `tests/meta/rc`; runtime command surface includes `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/022 -->
