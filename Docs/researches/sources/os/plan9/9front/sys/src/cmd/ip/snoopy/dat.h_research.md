# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dat.h

This is the core data header for snoopy protocol modules. It defines shared types `Proto`, `Mux`, `Field`, `Msg`, and `Filter`, plus network-byte-order macros `NetS`, `Net3`, and `NetL`.

`Proto` is the module vtable: name, compile hook, filter hook, print hook, mux table, value format, fields, and framer. `Mux` maps protocol names and numeric values to next `Proto` objects. `Field` describes filterable protocol fields.

`Msg` carries packet cursor state and print-buffer state during protocol walking. Modules advance `ps`, may truncate `pe`, set `pr` for the next protocol, and append to `p`.

`Filter` is the parsed filter-expression tree node. It stores operator, string token, child nodes, selected protocol, sub-operation, and typed comparison values.

The header also declares parser functions, compile/demux helpers, global display flags, and `filter`.
