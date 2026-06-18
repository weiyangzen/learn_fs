# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdfilt.h

## Role

`gsdfilt.h` defines the public interface for Ghostscript device filter stacks.

## Model

A device filter is a device-chain wrapper. Each pushed filter creates a new first device in the chain and forwards to its target; the physical page device remains at the end. A shadow stack node in the graphics state tracks the filter object and next device.

## Types

Forward-declares:

- `gs_device_filter_stack_t`
- `gs_device_filter_t`

Defines `struct gs_device_filter_s` with three callbacks:

- `push(self, mem, pgs, pdev, target)`
- `prepop(self, mem, pgs, dev)`
- `postpop(self, mem, pgs, dev)`

## API

Declares push, pop, and clear functions. Documents ownership expectations: `mem` is used to allocate/free filter stack state, and return values are Ghostscript error codes.

## Dependencies

Assumes `gs_state`, `gx_device`, `gs_memory_t`, and structure descriptors are available through included upstream headers.

## Risks

The callbacks define a low-level lifecycle contract but do not encode ownership or reference-count semantics in types. Filter implementations must coordinate carefully with graphics-state device refcounts.
