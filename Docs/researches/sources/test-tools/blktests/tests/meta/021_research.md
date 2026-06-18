<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/021 -->
# sources/test-tools/blktests/tests/meta/021

Purpose: blktests harness self-tests that verify skip and failure handling around `requires()`, `device_requires()`, and device-array entry points. This specific test is declared as: "exit with non-zero status from test_device_array()".

Important APIs/types/functions: sourced libraries `tests/meta/rc`; top-level variables `DESCRIPTION=exit with non-zero status from test_device_array()`; functions `test_device_array()` lines 11-15; external commands `echo`.

Control flow: `test_device_array()` uses commands `echo`.

State and persistence behavior: has no durable repository state; all observable state is temporary process, device, or build output handled by the caller.

Dependencies and integration points: integrates with the blktests `meta` suite and the shared harness; through `tests/meta/rc`; runtime command surface includes `echo`.

Risks and test signals: primary risk is build or harness drift; signal is make/shell exit status.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/meta/021 -->
