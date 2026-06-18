# File Research: sources/os/bsd/freebsd-src/sys/kern/pic_if.m

## Purpose
Declares the kobj interface for programmable interrupt controllers (PICs). It defines the interrupt-controller operations used by machine-independent interrupt code to map, activate, bind, enable, disable, service, and route interrupts and IPIs.

## Methods
- Interrupt lifecycle: `activate_intr`, `deactivate_intr`, `setup_intr`, and `teardown_intr`.
- Interrupt routing/control: `map_intr`, `bind_intr`, `enable_intr`, and `disable_intr`.
- Post/pre handling callbacks: `post_filter`, `pre_ithread`, and `post_ithread`.
- Secondary CPU setup: `init_secondary`.
- Interprocessor interrupts: `ipi_send` and `ipi_setup`.

## Defaults
The file provides no-op defaults for activation/deactivation/setup/teardown and secondary initialization, default unsupported returns for `bind_intr` and `ipi_setup`, and a no-op default for `ipi_send`. Core methods such as `map_intr`, `enable_intr`, `disable_intr`, and post/pre interrupt hooks must be supplied by concrete PIC implementations.

## Dependencies
Includes bus, cpuset, resource, and interrupt headers. The interface passes `struct intr_irqsrc`, `struct resource`, and `struct intr_map_data` objects, leaving controller-specific interpretation to implementers.

## Filesystem / VM Relevance
There is no direct filesystem behavior. The interface matters to the kernel execution substrate that storage controllers and block devices rely on for interrupts, especially on SMP systems with interrupt affinity and IPIs.
