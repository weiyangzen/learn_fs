# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_agents.h

## Role

`tavor_agents.h` defines the management-agent support layer for Tavor software-assisted InfiniBand agents, covering SMA/PMA/BMA-style MAD handling through IBMF.

## Major Definitions

The header defines default software-agent counts per port for QP0 and QP1. QP0 gets the SMA; QP1 currently registers one agent because firmware does not support BMA. It also defines the agent task queue thread count, maximum queued tasks, and base task queue name.

Directed-route MAD macros identify DR MADs, read hop count and hop pointer, update hop pointer, and set the direction bit with endian-specific status-bit handling. Additional macros identify special trap MADs and TrapRepress MADs.

`TAVOR_DRMAD_RETURN_PATH_OFFSET` gives the byte offset of the directed-route return path inside MAD data.

`tavor_agent_list_s` records driver state, port, management class, and IBMF handle for each registered agent so attach-time registrations can be cleaned up later. `tavor_agent_handler_arg_t` carries IBMF handle, message pointer, and agent-list pointer through the task queue from callback context to handler execution.

## Interfaces

The exported routines are `tavor_agent_handlers_init()` and `tavor_agent_handlers_fini()`.

## Integration Notes

This file bridges Tavor special-QP MAD traffic, IBMF agent registration, and task-queue-based request processing. It is only part of the control/management path, not data-path WQE posting.
