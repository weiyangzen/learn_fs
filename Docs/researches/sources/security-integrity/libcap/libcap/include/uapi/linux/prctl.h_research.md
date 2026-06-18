## sources/security-integrity/libcap/libcap/include/uapi/linux/prctl.h

Purpose: bundled subset of Linux `prctl` constants and structs required by libcap for process security state manipulation.

Important APIs/types/constants: `PR_SET_KEEPCAPS`, `PR_CAPBSET_READ`, `PR_CAPBSET_DROP`, `PR_GET_SECUREBITS`, `PR_SET_SECUREBITS`, `PR_SET_NO_NEW_PRIVS`, `PR_CAP_AMBIENT` and ambient subcommands, plus many adjacent `PR_*` definitions and `struct prctl_mm_map`.

Control flow: header constants only.

State/persistence: defines numeric ABI for `prctl()` calls used by `cap_proc.c`.

Dependencies/integration: Linux types header; used when system headers are unavailable or for bundled consistency.

Risks: stale or incorrect numeric constants would corrupt security-state calls; the file is not a complete modern prctl header beyond this snapshot.

Test signals: build libcap against bundled headers, run mode/ambient/bounding tests, and compare with system `linux/prctl.h` for relevant constants.
