## sources/security-integrity/audit-userspace/src/ausearch-checkpt.h

Purpose: public checkpoint interface and failure code definitions for `ausearch`.

Important APIs/types: declares `set_ChkPtFileDetails()`, `set_ChkPtLastEvent()`, `free_ChkPtMemory()`, `save_ChkPt()`, and `load_ChkPt()`. Defines failure bits `CP_NOMEM`, `CP_STATFAILED`, `CP_STATUSIO`, `CP_STATUSBAD`, and `CP_CORRUPTED`. Exports `checkpt_failure`, `chkpt_input_dev`, `chkpt_input_ino`, and `chkpt_input_levent`.

Control flow/state: `ausearch.c` treats `load_ChkPt()` return values below `-1` as fatal, `-1` as first run, and `0` as resume data present.

Dependencies/integration: includes `ausearch-llist.h` for `event` and system types for `dev_t`/`ino_t`.

Risks/test signals: consumers can mutate exported checkpoint globals directly. Tests should verify failure-bit propagation through `ausearch` exit codes 10, 11, and 12.
