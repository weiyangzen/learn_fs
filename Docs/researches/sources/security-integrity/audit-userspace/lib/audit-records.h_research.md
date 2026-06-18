# sources/security-integrity/audit-userspace/lib/audit-records.h

Purpose: Public header containing audit record type constants and fallback definitions for kernel/user-space audit message ranges.

Important constants: Defines user message ranges (`AUDIT_FIRST_USER_MSG`, `AUDIT_LAST_USER_MSG`), daemon messages, event ranges, SELinux, AppArmor, crypto, anomaly, anomaly response, LSPP, virtualization, and newer kernel record fallbacks such as `AUDIT_BPF`, `AUDIT_EVENT_LISTENER`, `AUDIT_URINGOP`, `AUDIT_OPENAT2`, `AUDIT_DM_CTRL`, `AUDIT_DM_EVENT`, and `AUDIT_ANOM_CREAT`.

Control flow: Preprocessor-only public ABI header with `extern "C"` guards. Uses `#ifndef` around newer kernel constants so system headers can provide canonical values.

State and persistence: No runtime state. It persists compile-time ABI for applications including libaudit headers.

Dependencies and integration: Includes `<linux/audit.h>` and is included by `audit_logging.h` and user applications. `libaudit.h` notes that record type definitions moved here as of audit 4.0.

Risks: Public header stability is critical. Wrong fallback numeric values break interoperability with kernel audit records and logs. It must not include private `gcc-attributes.h` because it is installed.

Test signals: Public header standalone compile in C and C++, comparison against current kernel audit constants, and application builds using `AUDIT_USER_*` and newer fallback constants.
