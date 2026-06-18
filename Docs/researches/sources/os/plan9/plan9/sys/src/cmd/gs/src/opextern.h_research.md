# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/opextern.h

Header declaring PostScript operator procedures that are referenced outside their defining translation units and are present in all Ghostscript interpreter configurations.

It groups exported `z*` and `zop_*` procedures by use:

- Special operator encoding in `interp.c`: arithmetic, stack, conditional, and dictionary primitives such as `zadd`, `zdef`, `zdup`, `zexch`, `zif`, `zifelse`, `zindex`, `zpop`, `zroll`, and `zsub`.
- Internal entry points: `zop_add`, `zop_def`, and `zop_sub`.
- Server loop, save/restore, graphics state, pagedevice, wrapper, specific-VM, user path, FunctionType 4, CIE cache, and miscellaneous support operators.
- Customer/special-use exports such as `zcurrentdevice`, `ztoken`, `ztokenexec`, and `zwrite`.

This is a cross-module interpreter declaration file, not OS or filesystem code.
