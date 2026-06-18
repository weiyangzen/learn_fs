# File Research: sources/virtualization/nbdkit/plugins/sh/call.h

Header for the shell invocation layer. It includes the nbdkit dynamic string type and `subplugin.h`, then declares `call`, `call_read`, and `call_write` with nonnull annotations.

These functions are the narrow interface between method dispatch code and the lower-level fork/exec/pipe machinery.
