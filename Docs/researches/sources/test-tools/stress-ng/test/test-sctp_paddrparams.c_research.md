<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_paddrparams.c -->
# sources/test-tools/stress-ng/test/test-sctp_paddrparams.c

Purpose: compile-time availability probe for `struct sctp_paddrparams` associated with `sctp_paddrparams`; the program mainly proves that the platform headers expose the type with a complete size.

Important APIs/types/functions: includes `netinet/sctp.h`; uses types `struct sctp_paddrparams`; defines `main`.

Control flow: `main()` initializes stack-local test objects, performs the probe calls, records return values only enough to keep the compiler from optimizing them away, and returns a simple status/value the success signal is the `sizeof` expression, forcing the type to be complete at compile time.

State and persistence behavior: runtime state is limited to stack variables, libc/kernel return values, and process-local descriptors or attributes. There is no intended persistent repository or host state.

Dependencies and integration points: depends on headers `netinet/sctp.h`. It integrates with stress-ng's configure/build tests, where compile/link/run success controls whether the corresponding stressor or code path is enabled.

Risks and test signals: SCTP structure probes depend on optional kernel/userland SCTP headers that are often packaged separately. Test signals are successful compilation; successful linking; a complete type size.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-sctp_paddrparams.c -->
