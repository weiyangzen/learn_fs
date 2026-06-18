# File Research: sources/virtualization/nbdkit/filters/rotational/rotational.c

This filter overrides the advertised rotational property. The `rotational=true|false` parameter is parsed as a boolean and defaults to true.

`.is_rotational` returns the configured value without delegating to the backend. The filter has no per-connection state and does not alter I/O behavior; it only shapes metadata that clients may use for scheduling or heuristics.
