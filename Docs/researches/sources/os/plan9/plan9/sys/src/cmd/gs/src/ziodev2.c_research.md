# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ziodev2.c

LanguageLevel 2 IODevice operators and `%null%` device definition. `%null%` accepts only write access and opens the platform null file through `file_open_stream`.

`.getdevparams` looks up an IODevice by string name, writes its parameters to the operand stack using `stack_param_list_write`, and prefixes the result with a mark. `.putdevparams` reads marked key/value parameters from the stack, checks the `SystemParamsPassword`, calls `gs_putdevparams`, releases parameter-list storage, and removes consumed operands.

The file is the PostScript parameter interface to `gx_io_device` implementations. It relies on the generic `gs_getdevparams`/`gs_putdevparams` hooks exposed by each device.
