# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_rseq.h

Reusable reversible-sequence helper interface for multistep driver setup/teardown. It models paired do/undo steps so attach-like code can unwind completed steps in reverse order after failure.

Defines function and callback signatures, callback return values (`RSEQ_OK`, `RSEQ_UNDO`, `RSEQ_ABORT`), step and sequence structures, `rseq_do()`/`rseq_undo()`, debug variants, failure-injection scenarios, and convenience macros for declaring step pairs.

The design is explicitly aimed at replacing goto/bitfield cleanup patterns in attach/detach implementations.
