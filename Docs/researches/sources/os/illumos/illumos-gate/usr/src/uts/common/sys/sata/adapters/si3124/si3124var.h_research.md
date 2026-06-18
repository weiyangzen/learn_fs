# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/si3124/si3124var.h

## Role

Private state and tunable header for the Silicon Image 3124 family SATA HBA driver.

## Key Elements

- Defines supported port counts for SI3124, SI3132, and SI3531.
- Defines return codes, log buffer size, timing/polling constants, and attach-progress flags.
- Defines SGT table limits and `SGE_LENGTH()` for chained scatter/gather capacity.
- `si_sgblock_t` is a logical wrapper around SGTs, allowing tunable chained S/G tables per PRB request.
- `si_event_arg_t` carries controller/port context for timeout callbacks.
- `si_portmult_state_t` tracks port-multiplier child port types.
- `si_port_state_t` holds per-port state: port type/activity, port-multiplier state, PRB and S/G pools plus DMA handles, mutex, pending tags, slot packet array, reset/mop/error-recovery state, and NCQ counters.
- `si_ctl_state_t` holds controller state: devinfo, port array, PCI config handle, BAR mappings, SATA HBA transport, timeout, interrupt handles, power and FMA capability state.
- Defines controller flags for PM, attach/detach, timeout suppression, and SATA framework attachment.
- Defines debug flags/macros and reset-control flags.

## Dependencies and Coupling

Depends on hardware structures from `si3124reg.h` and framework types from the SATA HBA layer. Warlock annotations document lock ownership and read-only fields.

## Research Notes

The driver tracks “mopping” operations for abort/reset/timeout/error recovery and uses that count to reject new `tran_start` work while cleanup is in progress. Port-multiplier state is deliberately compact because all child ports share one physical controller port.
