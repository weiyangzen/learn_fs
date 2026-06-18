# File Research: sources/os/plan9/9front/sys/src/cmd/rotate.c

`rotate.c` reads a Plan 9 image, rotates or flips it in memory, and writes the transformed image to stdout. It uses `memdraw` and operates on `Memimage` objects.

`rot90` rotates an image 90 degrees clockwise by allocating a destination image with swapped dimensions and copying each pixel's bytes into the transposed/reversed position. Low-bit grayscale formats (`GREY1`, `GREY2`, `GREY4`) are temporarily expanded to `GREY8`, then converted back to the original channel.

`upsidedown` vertically flips an image in place by swapping scanlines using a temporary line buffer.

Command options are `-r degree`, `-u`, and `-l`. Rotation is implemented by fall-through cases for `270`, `180`, and `90`, applying `rot90` repeatedly. `-l` combines vertical inversion with `180` degrees, producing the complementary orientation behavior expected by the tool.
