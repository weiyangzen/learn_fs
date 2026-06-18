# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdpnext.c

Implements NeXT Display PostScript extensions for alpha, compositing, and image sizing.

Key behavior:
- Provides `currentalpha`, `setalpha`, `.alphaimage`, `composite`, `compositerect`, `dissolve`, `.sizeimagebox`, and `.sizeimageparams`.
- Builds temporary alpha compositor devices around fill/image operations and restores the original device afterward.
- `composite`/`dissolve` copy source rectangles from another gstate or current gstate to a destination point.
- `.sizeimagebox` transforms and clips a source rectangle to device coordinates, returning a matrix adjusted to the clipped box.
- `.sizeimageparams` derives bits/sample, multiproc flag, and component count from the current device.
- Includes true-color detection for grayscale, RGB, and CMYK devices by testing device color mapping.

Dependencies:
- Uses compositor device creation, ImageType 2 processing, current matrix/path state, device color mapping, and imager alpha APIs.

Research notes:
- Composite setup/teardown is delicate because it swaps current devices temporarily and must close/free compositor devices on all paths.
