# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscparam.c

## Purpose
Default in-memory implementation of Ghostscript parameter lists.

## Key Behavior
- Defines `gs_c_param` entries and `gs_c_param_list` GC descriptors.
- Supports writing typed parameters into a linked list.
- Supports nested dictionaries, integer-key dictionaries, and arrays via child `gs_c_param_list` objects.
- Deep-copies nonpersistent strings, names, int arrays, float arrays, string arrays, and name arrays.
- Tracks requested-but-unwritten parameters using `gs_param_type_any`.
- Supports delegated requested checks through an optional target parameter list.
- Switches lists from write mode to read mode through `gs_c_param_list_read`.
- Reads typed parameters, including nested collections and target fallback.
- Provides int-array to float-array alternate conversion storage for compatible reads.
- Enumerates keys and provides simple read policy/signal/commit hooks.

## Important Details
- `gs_c_param_list_release` recursively frees collection parameters and nonpersistent copied data.
- Nonpersistent string arrays allocate one combined block for array elements plus second-level string data.
- Request tracking distinguishes “requested but undefined” from actual written parameters.
- The implementation assumes parameter lists are transient enough that some allocated blocks do not need rich GC descriptors.

## Dependencies
Uses Ghostscript parameter-list APIs, memory allocation, string helpers, GC relocation/enumeration macros, and error codes.

## Research Notes
This is generic infrastructure heavily used by device parameter serialization, including CRD parameter read/write code in `gscrdp.c`.
