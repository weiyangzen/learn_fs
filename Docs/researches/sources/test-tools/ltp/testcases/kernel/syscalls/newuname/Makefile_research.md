# sources/test-tools/ltp/testcases/kernel/syscalls/newuname/Makefile

Purpose: generic LTP build leaf for the `newuname`/`uname` test. Important APIs/types/functions: common make includes. Control flow: no local flags or targets; standard rules build `newuname01`. State/persistence: only build products. Dependencies/integration: integrates the raw `uname` syscall test into LTP's kernel syscall suite. Risks: no special handling for architecture-specific machine field is needed at build time. Test signals: successful build indicates common rules compile the test.
