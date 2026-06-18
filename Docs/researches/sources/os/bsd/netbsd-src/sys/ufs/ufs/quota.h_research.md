# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota.h

This header defines quota constants common to quota1 and quota2.

Key contents:
- Defines two quota slots: user and group.
- Defines quota name initializer strings.
- Provides conversion helpers between generic quota id types and UFS quota slots.
- Declares quota subsystem init/reinit/done functions under `_KERNEL`.

Role:
- Common quota vocabulary used by both legacy quota files and newer metadata-backed quotas.
