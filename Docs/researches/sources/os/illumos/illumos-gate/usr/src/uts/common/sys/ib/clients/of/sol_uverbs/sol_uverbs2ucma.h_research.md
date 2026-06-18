# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs2ucma.h

This small inter-driver contract header declares the sol_uverbs symbols that sol_ucma dynamically uses.

Core definitions:
- `SOL_UCMA_UVERBS_PATH` names the UCMA access path through sol_uverbs.
- Named symbol strings and function pointer typedefs expose:
  - IB/iWARP client handle retrieval.
  - QP-number to QP-handle lookup.
  - Disabling user QP modification.
  - Enabling/disabling CQ notification for CQs associated with a QP.
  - Setting QP free state.
  - Flushing a QP.
- `sol_uverbs_cq_ctrl_t` models CQ notification not-set/enable/disable.
- `sol_uverbs_qp_free_state_t` models enable free, disable free, and free pending.

Risk-sensitive invariants:
- This is a runtime symbol ABI between two kernel drivers; names and signatures must stay stable.
- CQ notification gating exists to ensure the first user completion is delivered only after connection establishment.
- QP free-state control prevents UCMA and uverbs from racing connection teardown against user QP destruction.
