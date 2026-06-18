<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/Makefile.am -->
# sources/security-integrity/audit-userspace/src/test/Makefile.am

**Purpose**
This Automake fragment defines the audit-userspace source-level unit and regression tests for list helpers, audit event formatting, and allocation failure handling in auditd configuration parsing.

**Important APIs, Types, And Functions**
It sets shared include paths to the top source tree, `lib`, and `src`, enables `_GNU_SOURCE`, and conditionally adds ASAN flags. `check_PROGRAMS` and `TESTS` contain `ilist_test`, `slist_test`, `format_event_test`, and `auditd_config_alloc_test`. The list tests link prebuilt object files `ausearch-int.o` and `ausearch-string.o`; `format_event_test` compiles several auditd source files directly and links `libaudit`, `libauparse`, `libdisp`, libev, common helpers, pthread, math, GSS, and tcp-wrappers when configured. `auditd_config_alloc_test` is a standalone include-based harness.

**Control Flow**
During `make check`, Automake builds all four programs and executes each as a test. Conditional `ENABLE_LISTENER` adds `auditd-listen.c` to the format-event test source set.

**State And Persistence**
No runtime persistence is introduced by the makefile. It does control build-time state such as object dependencies and ASAN instrumentation.

**Dependencies And Integration Points**
The file integrates test binaries with the larger audit-userspace build graph and shares flags with configured sanitizer support.

**Risks**
The `format_event_test` target depends on many daemon internals, so changes in auditd source dependencies can break linking. The allocation test includes a C implementation file directly, which is intentional but couples the test to static/internal symbols.

**Test Signals**
The file itself is the test registration point; successful `make check` means all four harnesses were compiled and run under the configured feature set.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/test/Makefile.am -->
