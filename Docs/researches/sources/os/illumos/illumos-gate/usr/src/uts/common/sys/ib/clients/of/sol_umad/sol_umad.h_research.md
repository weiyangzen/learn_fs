# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_umad/sol_umad.h

This Solaris UMAD driver header defines user MAD contexts, agents, HCA/port state, IBMF registration records, message wrappers, and driver entry points.

Core definitions:
- Minor-number macros encode node, port, ISSM status, and user context number.
- Only one UMAD instance is supported; up to 16 user contexts are tracked.
- `umad_uctx_t` represents an open file context with registered agents, receive queue, pollhead, and CV.
- `umad_agent_t` records MAD registration request, IBMF registration, owning user context, outstanding messages, lock/CV, and unregister/async flags.
- `umad_hca_info_t` and `umad_port_info_t` describe HCA GUIDs/handles/attributes and per-port minor nodes, GUID/LID, ISSM open count, and IBMF registrations.
- `umad_info_t` is global driver state: devinfo, mutex, IBT client handle, HCA GUID/info arrays, and open contexts.
- `ib_umad_msg_t`, `umad_send`, and `ibmf_reg_info` bridge user MAD buffers to IBMF messages and registrations.

Risk-sensitive invariants:
- Agent unregister must wait for outstanding messages and async handling to drain.
- Receive queues and agent lists have separate locks.
- Minor encoding leaves room for 16 boards and 16 ports, with ISSM marked by a high bit.
