# File Research: sources/os/plan9/9front/sys/src/cmd/cc/pickle.c

Generates acid/pickle helper output for compiler `-Z` debug/introspection mode.

Key behavior:
- Maintains acid keyword escaping through `pmap`.
- `picklesue` finds the symbol naming a struct/union/enum tag for a type.
- `picklefun` finds the symbol associated with a function type.
- `pickleinit` maps compiler primitive type codes to pickle format characters, adapting `int`/`uint` to target width.
- `picklemember` emits C statements that serialize primitive, pointer, array, struct, and union members.
- `pickletype` emits `pickle_<type>` functions for structs/unions, or structure offset defines under `-s`.
- `picklevar` emits acid declarations for globals, statics, autos, params, and enum constants when `-Z` is active.

Dependencies:
- Includes `cc.h`.
- Writes generated text to `outbuf`.
- Uses compiler symbol hash, current input stack, current function, and type metadata.

Research notes:
- This is compiler-generated debugging/introspection support, not runtime serialization used by compiled programs.
- It deliberately skips nested include contexts when `debug['Z'] > 1`.
