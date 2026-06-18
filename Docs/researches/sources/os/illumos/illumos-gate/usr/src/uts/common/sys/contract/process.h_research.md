# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/process.h

This header defines the process-contract public ABI. It names default service FMRI values, process contract parameters (`INHERIT`, `NOORPHAN`, `PGRPONLY`, `REGENT`), event masks (`EMPTY`, `FORK`, `EXIT`, `CORE`, `SIGNAL`, `HWERR`), all-event/all-fatal masks, parameter ids, status field names, and event field names for pid, parent pid, core files, signal, sender, sending contract, and exit status.

It forward-declares process template and contract structures and depends on the generic contract header plus time definitions.
