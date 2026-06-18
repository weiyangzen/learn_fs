# File Research: sources/os/linux/linux/fs/isofs/rock.h

Defines packed on-disk SUSP/Rock Ridge structures used by `rock.c`.

Structures include:
- SUSP records: `SU_SP_s`, `SU_CE_s`, `SU_ER_s`
- Rock Ridge records: `RR_RR_s`, `RR_PX_s`, `RR_PN_s`, `RR_SL_s`, `RR_NM_s`, `RR_CL_s`, `RR_PL_s`, `RR_TF_s`
- Linux zisofs extension: `RR_ZF_s`
- `struct rock_ridge`, a common signature/length/version header plus union of record payloads.

Defines timestamp flags `TF_*` and Rock Ridge presence flags `RR_PX`, `RR_PN`, `RR_SL`, `RR_NM`, `RR_CL`, `RR_PL`, `RR_RE`, and `RR_TF`.
