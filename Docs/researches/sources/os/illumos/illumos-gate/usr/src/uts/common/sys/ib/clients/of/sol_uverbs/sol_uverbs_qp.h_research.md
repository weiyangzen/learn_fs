# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_qp.h

This sol_uverbs QP/SRQ command header declares queue-pair and shared-receive-queue handlers plus multicast attach/detach support.

Core definitions:
- `IBT_TO_OFA_QP_STATE()` maps IBTF states into OFA QP states, collapsing SQ-drain variants to `IB_QPS_SQD`.

API surface:
- Create, destroy, modify, and query QP.
- Create, modify, query, and destroy SRQ.
- Attach and detach multicast.
- Detach all multicast entries owned by a user QP.

Risk-sensitive invariants:
- QP modification may be disabled by UCMA while connection manager owns transitions.
- Multicast memberships attached to a QP must be detached during QP cleanup.
- QP state translation assumes OFA and IBTF state ordering up to SQ-drain.
