# File Research: sources/os/bsd/netbsd-src/lib/libc/include/isc/assertions.h

ISC assertion interface used by imported resolver/event code.

Defines:
- `assertion_type` enum: require, ensure, insist, invariant.
- `assertion_failure_callback`.
- Global callback `__assertion_failed`.
- `set_assertion_failure_callback` and `assertion_type_to_text`.

Macros:
- `REQUIRE`, `ENSURE`, `INSIST`, `INVARIANT` and `_ERR` variants.
- Check enablement is controlled by `CHECK_ALL`, `CHECK_NONE`, `_DIAGNOSTIC`, and Coverity.
- Disabled macros still evaluate conditions except lint-specific `INSIST`.

Failure path delegates to `__assertion_failed`.
