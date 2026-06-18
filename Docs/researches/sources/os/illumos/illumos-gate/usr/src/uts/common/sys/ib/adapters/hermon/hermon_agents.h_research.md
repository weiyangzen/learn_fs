# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_agents.h

## Role

`hermon_agents.h` defines the Hermon InfiniBand management-agent support interface for SMA/PMA/BMA-related handling through IBMF.

## Key Interfaces and Data

- Defines default software-assisted agent counts: one QP0 agent per port and one QP1 agent per port. Comments note QP1 would normally include PMA and BMA, but Hermon firmware does not support BMA registration here.
- Agent task queue sizing uses one thread and at most four queued tasks.
- Task queue base name is `hermon_taskq`, later combined with instance number.
- Directed-route MAD macros detect DR MADs, get hop count/pointer, set hop pointer, and set direction with endian-specific status bits.
- Trap macros detect special Hermon trap MADs and TrapRepress MADs.
- `HERMON_DRMAD_RETURN_PATH_OFFSET` defines the return-path offset in directed-route MAD data.
- `hermon_agent_list_s` stores per-agent list linkage, IBMF handle, port, QP number, and management class.
- `hermon_agent_handler_arg_s` packages state, port, QP number, management class, and IBMF handle for asynchronous agent handlers.
- Declares `hermon_agent_handlers_init()` and `hermon_agent_handlers_fini()`.

## Dependencies and Use

The header includes DDI types and IBMF management headers. It is used by Hermon agent implementation files and relies on `hermon_state_t` from the main driver header.

## Research Notes

The macros encode MAD protocol details directly in the header, especially endian-sensitive directed-route status manipulation.
