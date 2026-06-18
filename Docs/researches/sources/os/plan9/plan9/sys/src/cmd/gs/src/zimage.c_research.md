# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zimage.c

Core image operator implementation for `.image1`, `.imagemask1`, and shared image data feeding. It parses image dictionaries, starts graphics-library image enumerators, and drives those enumerators from procedure, string, or file data sources.

`data_image_params` validates common image dictionary keys: `Width`, `Height`, `ImageMatrix`, `MultipleDataSources`, `BitsPerComponent`, `Decode`, `Interpolate`, and `DataSource`. `pixel_image_params` adds current color-space component count, rejects Pattern color space, sets chunky vs component-planar format, and reads `CombineWithColor`.

`zimage_setup` starts a typed image with `gs_image_begin_typed`, then `zimage_data_setup` allocates a local image enumerator and pushes execution-stack control records. The control records store source refs, aliasing info for repeated file sources, current plane index, plane count, and the enumerator.

There are three continuation paths. Procedure sources call the source procedure for each wanted plane and accept returned strings. File sources buffer and skip stream data, handle EOF and stream exceptions, and account for aliasing when the same file appears multiple times. String sources feed complete strings and may still return for `e_RemapColor` callbacks. `image_cleanup` releases the enumerator. This file is a key state-machine boundary between PostScript execution and incremental image rendering.
