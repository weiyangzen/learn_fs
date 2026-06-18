# sources/security-integrity/selinux/libsepol/cil/test/unit/test_integration.c

Purpose: Provides integration tests comparing secilc-generated policy output with checkpolicy output and compiling a minimal CIL policy.

Important APIs and functions: `test_integration()` invokes `system()` for `./secilc -M -c 24 test/integration.cil`, `checkpolicy -M -c 24 -o policy.conf.24 test/policy.conf`, and `sediff -q policy.24 ; policy.conf.24`; `test_min_policy()` invokes secilc on `test/policy.cil`.

Control flow: Each command is run through the shell with output redirected to `/dev/null`; signal exits for SIGINT/SIGQUIT print diagnostics; CuTest asserts normal exit and status zero.

State and persistence: Commands create or consume policy artifacts in the working directory, especially `policy.24` and `policy.conf.24`. No cleanup is performed here.

Dependencies and integration points: Requires built `secilc`, external `checkpolicy` and `sediff`, and test policy files.

Risks: Shell redirection is non-portable to non-sh shells, and command availability/path assumptions make this more environment-sensitive than pure unit tests.

Test signals: Zero exit from secilc, checkpolicy, and sediff indicates CIL compilation matches reference policy semantics for the fixture.
