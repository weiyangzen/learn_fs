# sources/security-integrity/selinux/sandbox/sandbox.conf
# sources/security-integrity/selinux/sandbox/sandbox.conf

Purpose: cgroup-style resource configuration for sandbox.

Important content and control flow: defines `NAME=sandbox`, `CPUAFFINITY=ALL`, `MEMUSAGE=80%`, and `CPUUSAGE=80%`.

State and persistence: installed under sysconfig as `sandbox`; consumed by sandbox/cgroup integration outside this file.

Dependencies and integration points: referenced by sandbox packaging and likely system policy/scripts for resource limits.

Risks and test signals: file itself has no validation; if downstream parsers expect stricter syntax, malformed changes would affect sandbox limits. No direct tests.
