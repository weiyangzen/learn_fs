# File Research: sources/virtualization/nbdkit/filters/noextents/noextents.c

This minimal filter disables extent support by implementing `.can_extents` to return `0`. It registers the filter under the name `noextents` and otherwise leaves all operations to normal nbdkit filter fallback behavior.

The effect is capability shaping: clients will not see block-status/extents support even if the underlying plugin supports it. There is no per-connection state and no request-path transformation.
