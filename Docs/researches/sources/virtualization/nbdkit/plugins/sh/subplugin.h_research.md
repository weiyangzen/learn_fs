# File Research: sources/virtualization/nbdkit/plugins/sh/subplugin.h

Defines the shared abstraction used by `nbdkit-sh-plugin` and the related eval plugin. It declares shell-script exit codes for OK, error, missing method, false, shutdown, and disconnect behaviors, reserving codes 9-15 for future handling as errors.

`struct subplugin` provides callbacks for resolving the script for a method and for invoking methods with no output, captured stdout, or stdin payload. The global `sub` lets shared method-dispatch code call either the shell plugin's process runner or another compatible subplugin backend.
