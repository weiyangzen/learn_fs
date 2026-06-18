# sources/user-network-fs/nfs-ganesha/src/SAL/CMakeLists.txt

Purpose: defines the SAL object library source composition for state management, NFSv4 client/session/lease/recovery logic, optional NLM and 9P state support, and optional RADOS recovery module.

Important APIs and targets: `sal_STAT_SRCS`, `add_library(sal OBJECT ...)`, `add_sanitizers(sal)`, `set_target_properties(... -fPIC)`, feature variables `USE_NLM`, `USE_9P`, `USE_RADOS_RECOV`, and `USE_LTTNG`, plus module target `ganesha_rados_recov`.

Control flow: starts with core SAL sources, appends NLM owner/state sources when NLM is enabled, appends `9p_owner.c` when 9P is enabled, builds the `sal` object library, attaches sanitizer and PIC properties, and wires trace header dependencies. If RADOS recovery is enabled, it builds a separate module from RADOS recovery sources, links it against `ganesha_nfsd`, system/RADOS libraries, and disallow-undefined flags, includes RADOS headers, sets SOVERSION, and installs it.

State and persistence: no runtime state. Build-time feature selection determines which state-management implementations and recovery plugins are available.

Dependencies and integration points: central build integration point for SAL, NFSv4 recovery, optional NLM/9P, LTTng, and RADOS recovery. Must match config headers and runtime feature assumptions.

Risks: feature gates must align with source references elsewhere; enabling `USE_9P`, `USE_NLM`, or `USE_RADOS_RECOV` without dependencies can fail compilation/linking. The RADOS module links against the main daemon and external libraries, so ABI and undefined-symbol handling are important.

Test signals: matrix builds for NLM/9P/RADOS/LTTng combinations, final target link checks, module install verification for RADOS recovery, and startup tests confirming the selected state/recovery backends initialize.
