# sources/security-integrity/selinux/python/sepolgen/tests/test_policygen.py

## Purpose
This file tests conversion from access vectors into reference-policy module rules by `sepolgen.policygen.PolicyGenerator`, including optional extended-permission rule generation.

## Important Tests And Exercised APIs
`test_init()` verifies `PolicyGenerator.xperms` defaults to false. `test_set_gen_xperms()` checks toggling extended-permission generation. `test_av_rules()` builds three same-source/same-target file permissions and asserts `add_access()` emits one `refpolicy.AVRule` with sorted permissions in the module.

`test_ext_av_rules()` enables xperms, builds file and dir ioctl access vectors with `XpermSet` values, adds them to an `AccessVectorSet`, and verifies the module contains both plain `AVRule` and `AVExtRule` objects per class with correct source, target, class, operation, rule type, and merged ranges.

## Control Flow
Each test creates access vectors and an `AccessVectorSet`, calls `PolicyGenerator.add_access()`, then inspects `self.g.module.children`. The xperm test manually classifies resulting children by type and object class because rule ordering is not assumed.

## State And Persistence
State lives in the `PolicyGenerator` instance and its in-memory module tree. No files are written by these tests.

## Dependencies And Integration Points
It depends on `sepolgen.policygen`, `sepolgen.access`, and `sepolgen.refpolicy`. It validates the downstream consumer of audit/access-vector generation and upstream producer of SELinux policy source rules.

## Risks And Edge Cases
The plain AV rule test asserts an exact string, so it relies on deterministic permission ordering. The xperm test is more robust about rule ordering but still assumes class partitioning is unambiguous. It does not test dontaudit, interface generation, module headers, or full policy serialization.

## Test Signals
The file provides strong signals for plain allow generation and ioctl xperm generation, including range merging and separation by object class.
