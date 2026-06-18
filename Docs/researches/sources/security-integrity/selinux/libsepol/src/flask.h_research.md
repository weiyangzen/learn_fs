# sources/security-integrity/selinux/libsepol/src/flask.h

Purpose: generated header defining numeric initial security identifier constants for SELinux policydb use. It provides stable indices for kernel, security, unlabeled, filesystem, networking, sysctl, module, policy, packet, and device-null initial SIDs.

Important APIs and types: constants `SECINITSID_KERNEL` through `SECINITSID_DEVNULL` assign one-based SID values, and `SECINITSID_NUM` records the maximum known SID count.

Control flow: none; this is a compile-time constant header.

State and persistence behavior: no runtime state. The numeric values are part of the binary/textual policy contract and must remain aligned with generated SID-name tables and kernel expectations.

Dependencies and integration points: included by policydb and conversion code that needs known initial SID numbers. It complements generated SID name arrays used by kernel-to-CIL/conf conversion and initial SID context handling.

Risks: manual edits would desynchronize libsepol from generated Flask/security class data. Off-by-one mistakes are especially risky because SIDs are one-based in policy structures.

Test signals: build-time generated-header consistency checks, policy read/write round trips with all known initial SIDs, and conversion output that preserves SID declaration/order and context mapping.
