# File Research: sources/os/bsd/dragonflybsd/sys/sys/fbio.h

`fbio.h` defines framebuffer and video-adapter ioctl structures and constants. It includes `sys/types.h`, `sys/ioccom.h`, and `machine/types.h`.

The older framebuffer interface includes framebuffer type IDs, `struct fbtype`, color-map structures, framebuffer attributes, video on/off control, hardware cursor structures, and corresponding `FBIO*` ioctls. The newer interface defines `video_info_t`, `video_adapter_t`, `video_adapter_info_t`, display-start and palette structures, VGA/EGA/Hercules mode numbers, adapter flags, memory model constants, and more `FBIO_*` control commands.

This is a device ABI header. Structures contain user pointers for colormap/cursor/palette buffers, so ioctl handlers must validate and copy data carefully.
