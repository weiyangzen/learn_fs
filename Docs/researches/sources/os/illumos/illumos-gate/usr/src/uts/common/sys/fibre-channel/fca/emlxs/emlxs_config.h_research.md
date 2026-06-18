# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_config.h

## Purpose

`emlxs_config.h` defines driver tunable metadata and, when `DEF_ICFG` is set, the default configuration table for the Emulex FCA driver.

## Main Types

`emlxs_config_t` stores one tunable: name string, low/high/default/current values, flags, and help text.

`emlxs_cfg_parm_t` enumerates all tunable parameters. They cover console/log verbosity, IOCB and transfer sizing, unsolicited buffers, network-on, ACK0, topology, link speed, node count, interrupt coalescing delay/count, ALPA assignment, ADISC, power management, firmware checks, discovery/link/offline timeouts, LILP, PCI max read, heartbeat/reset/timeout controls, I/O tags, dynamic memory, FMA, MSI, SLI mode, NPIV, DH-CHAP authentication, target mode, work queues, persistent linkdown, patch enablement, target reset behavior, FCoE FCF timing, delayed discovery, request recovery qualifier mode, and performance hints.

## Constants and Tables

`EMLXS_CFG_STR_SIZE` is 32 and `EMLXS_CFG_HELP_SIZE` is 81.

`PARM_HIDDEN` marks hidden parameters; other flag names such as dynamic, reset, link, boolean, and hex are consumed from surrounding driver headers.

When `DEF_ICFG` is defined, `emlxs_cfg[]` must be in the exact enum order and provides min/max/default/flags/help text for every enabled parameter, with conditional entries for node throttle, FMA, max RRDY, MSI, DHCHAP, and SFCT.

## Research Notes

This is the driver’s configuration schema. Storage behavior affected here includes maximum I/O size, link topology/speed, discovery timing, NPIV virtual ports, authentication, FCoE failover timing, target mode, and persistent link state.
