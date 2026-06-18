# sources/security-integrity/audit-userspace/rules/41-containers.rules

Purpose: logs container creation and configuration-related namespace operations.

Important rules: b32/b64 `clone` rules with namespace flag mask `a0&0x7C020000` key `container-create`, and b32/b64 `unshare,setns` rules key `container-config`.

Control flow: syscall exit filters.

State and persistence: kernel audit rules.

Dependencies and integration: architecture syscall tables and argument bit-test parsing.

Risks and test signals: clone flag masks may not cover all container runtimes or newer clone3 paths. Test by starting a container and searching container keys.
