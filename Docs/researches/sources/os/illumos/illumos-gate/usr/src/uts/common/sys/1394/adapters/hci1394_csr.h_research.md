# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_csr.h

Private interface and state for IEEE 1394 CSR registers implemented in software by the HAL. Hardware-backed CSR registers live in the OHCI layer; this header covers software register storage, split-timeout handling, bus-reset state, and accessors.

Key elements:
- Documents CSR context from IEEE 1212, IEEE 1394-1995, and P1394A.
- Explains split timeout representation in 1394 bus cycles and its split into `split_timeout_hi` and `split_timeout_lo`, including legal low-register bounds of 800 to 7999 cycle units.
- Notes the inherent race when updating split timeout through two non-atomic CSR writes.
- Defines CSR register address offsets for state clear/set, node IDs, reset start, split timeout hi/lo, cycle/bus/busy time, bus manager ID, bandwidth available, and channel availability registers.
- `hci1394_csr_t` stores software CSR state, split timeout in observed cycles, previous-root state, node capabilities, OHCI handle, driver info pointer, and mutex.
- Defines opaque `hci1394_csr_handle_t`.
- Declares lifecycle functions: `hci1394_csr_init()`, `hci1394_csr_fini()`, and `hci1394_csr_resume()`.
- Declares accessors for node capabilities, CSR state get/set/clear, split-timeout hi/lo get/set, combined split-timeout get, and bus-reset handling.

Dependencies:
- Depends on DDI headers and adapter definitions for `hci1394_ohci_handle_t` and `hci1394_drvinfo_t`.
- Integrated with async transaction timeout behavior and OHCI CSR/hardware register support.

Research notes:
- The implementation behind this header must clamp split-timeout writes to legal 1394 values.
- The exposed `hci1394_csr_bus_reset()` suggests CSR state is refreshed or adjusted on bus reset, including root-status tracking.
