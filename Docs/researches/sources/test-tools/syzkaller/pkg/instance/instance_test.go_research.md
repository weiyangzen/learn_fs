## sources/test-tools/syzkaller/pkg/instance/instance_test.go

Purpose: verifies formatted command lines for syz-execprog and runner invocations.

Important APIs/types/functions: `TestExecprogCmd` and `TestRunnerCmd`.

Control flow: constructs representative `csource.Options` and expected command strings across repeat, sandbox, threaded/collide, fault, optional flag, host-fuzzer OS, coverage, and runner cases.

State and persistence: none.

Dependencies and integration: asserts the string contract consumed by VM command execution.

Risks: command tests can be brittle but catch accidental flag/order changes. They do not execute commands.

Test signals: good regression signal for compatibility with old/new syz-execprog flags.
