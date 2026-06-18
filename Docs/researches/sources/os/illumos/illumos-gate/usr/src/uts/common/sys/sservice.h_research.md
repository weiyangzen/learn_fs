# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sservice.h

## Role

PCMCIA Socket Services/Card Services interface definitions for adapters, sockets, windows, events, and resource allocation.

## Key Contents

Defines Socket Services function identifiers, Card Services helper identifiers, return codes, card/socket events, event masks, and registration structure `csregister_t`.

Provides data structures for getting and setting adapter, page, socket, status, and window state. Defines IRQ, page, socket, interface, DMA, power, resource, window, and voltage flags. Includes inquiry structures for adapter/socket/window capabilities, memory and I/O window characteristics, IRQ handler registration, device-node creation, adapter info, cookies/DIP retrieval, and reset modes.

Defines the `sservice_t` union over exported request structures and event-manager `pcm_make_dev`.

## Kernel Interfaces

Under `_KERNEL`, declares PCMCIA nexus attach/control/property/intr/open/close/ioctl/power/resume/wait functions and resource allocation, free, map, and bus-map helpers.

## Design Notes

This is a legacy but broad hardware-management ABI. It combines service dispatch IDs, event callbacks, device-node operations, and resource allocation contracts in one header.
