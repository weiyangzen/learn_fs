# sources/security-integrity/audit-userspace/rules/21-no32bit.rules

Purpose: detects use of 32-bit syscall ABI on a 64-bit platform as a possible exploitation signal.

Important rule: `-a always,exit -F arch=b32 -S all -F key=32bit-abi`.

Control flow: loaded as a single exit filter rule.

State and persistence: kernel audit rule state after load.

Dependencies and integration: relies on architecture parsing in libaudit and kernel compat syscall auditing.

Risks and test signals: noisy on systems legitimately running 32-bit binaries; invalid on pure 32-bit systems. Test with a 32-bit executable and search for key `32bit-abi`.
