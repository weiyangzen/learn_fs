# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/tpmif.h

Imported Xen public TPM/vTPM protocol ABI.

Purpose:
- Defines Xen TPM frontend/backend request structures, including older single-request ring and v2 shared-page state machine.

Key content:
- Defines `struct tpmif_tx_request`, one-entry TPM ring, and `tpmif_tx_interface`.
- Documents v2 passive TPM request/response behavior with submit/finish/cancel/idle state changes.
- Defines `enum tpmif_state`.
- Defines `struct tpmif_shared_page` with length, state, locality, extra page count, and flexible grant list.

Integration:
- Not used by visible 9front Xen runtime code.
- Vendored for Xen public device protocol completeness.

Risks/notes:
- Long TPM packets use extra grants that must be mapped contiguously by the backend.
- State transitions are asymmetric by design: frontend submits/cancels, backend idles/finishes.
