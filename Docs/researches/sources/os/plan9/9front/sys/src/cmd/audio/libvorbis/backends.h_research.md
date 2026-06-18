# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/backends.h

## Role

This private libvorbis header defines backend function tables and static configuration structures for floors, residues, and mappings. It is needed by static mode headers and backend implementations.

## Floor Backend

`vorbis_func_floor` contains function pointers for packing, unpacking, lookup creation, cleanup, and inverse floor reconstruction.

Floor configuration structs include:

- `vorbis_info_floor0`: order, rate, Bark map, amplitude settings, codebook list, and encode-side threshold hints.
- `vorbis_info_floor1`: partition classes, subclass books, multiplier, post list, and encode-side fitting parameters.

## Residue Backend

`vorbis_func_residue` defines packing, unpacking, lookup, cleanup, classification, forward, and inverse callbacks.

`vorbis_info_residue0` describes block-partitioned vector-quantized residue coding, including begin/end, grouping, partition count, groupbook, second-stage flags, book list, and encode classification metrics.

## Mapping Backend

`vorbis_func_mapping` defines mapping pack/unpack/free plus forward and inverse processing.

`vorbis_info_mapping0` stores submap routing, channel muxing, floor/residue submap indexes, and channel coupling configuration.

## Integration Notes

This header is ABI-internal to libvorbis. It ties codec setup data to the runtime backend registries `_floor_P`, `_residue_P`, and `_mapping_P`.
