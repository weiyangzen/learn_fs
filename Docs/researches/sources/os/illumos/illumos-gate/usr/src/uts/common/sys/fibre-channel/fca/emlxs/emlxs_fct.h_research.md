# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fct.h

Purpose: Provides conditional COMSTAR/FCT target-mode integration declarations and compatibility definitions for the Emulex driver.

Key definitions:
- Entire functional content is gated by `SFCT_SUPPORT`.
- Includes illumos kernel headers and COMSTAR headers `<sys/stmf.h>` and `<sys/fct.h>`.
- Undefines `FC_WELL_KNOWN_ADDR` before including FCT to avoid macro conflicts.
- Provides fallback definitions for newer link/port speeds if not already present: 8G, 10G, 16G, 32G.
- `EMLXS_FCT_NUM_ELS_ONLY` is 8, for ports that only send ELS commands and do not need valid command handles.
- Without `MODSYM_SUPPORT`, declares weak references for FCT/STMF entry points and `stmf_alloc`/`fct_alloc`.

Dependencies and interactions:
- `emlxs_fc.h` embeds extensive FCT state in `emlxs_buf_t`, `emlxs_port_t`, and target statistics under `SFCT_SUPPORT`.
- `emlxs_extern.h` declares target-mode implementation hooks under `SFCT_SUPPORT`.

Implementation notes:
- This header lets the same driver build with or without target-mode support.
- Weak symbols support optional linkage when dynamic symbol loading is not used.
