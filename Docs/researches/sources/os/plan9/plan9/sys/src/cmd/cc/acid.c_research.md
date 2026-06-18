# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/acid.c

Plan 9 C compiler support for emitting Acid debugger type information. It maps C aggregate/member types into Acid `aggr`, `complex`, and printer definitions when debug flag `a` is enabled.

`amap` avoids Acid keyword conflicts by mapping reserved names to `$`-prefixed forms. `acidsue` and `acidfun` search compiler symbol hashes for struct/union tags and functions. `acidmember` emits aggregate member metadata or print code depending on mode.

`acidtype` emits Acid aggregate definitions or, with debug `s`, assembler-style `#define` offsets. `acidvar` emits `complex` bindings for locals, parameters, globals, and enum constants when the variable’s type is a struct/union or pointer thereto.
