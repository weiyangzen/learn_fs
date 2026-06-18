# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/boot.c

El Torito boot support for ISO 9660 images.

`Cputbootvol` writes a boot record volume descriptor with `EL TORITO SPECIFICATION` and reserves a pointer location for the boot catalog. `Cupdatebootvol` later patches that pointer with `cd->bootcatblock`.

`Cputbootcat` writes the boot catalog validation header and records `bootimageptr` for later patching. `Cupdatebootcat` writes the initial/default boot entry: bootable flag, emulation type or no-emulation, load segment, sector count, and boot image block. No-emulation images are limited to loading at most four 512-byte sectors with a warning.

`Cfillpbs` patches a Plan 9 PBS boot image with loader block and size metadata. `findbootimage` and `findloader` locate named files in the staged `Direc` tree and store pointers in `Cdimg`.

Integration points: invoked from `createcd` and `dump9660.c` when boot flags are set; depends on directory block assignments from `writefiles`.

Risks and notes: boot catalog fields are patched after the boot image is discovered. Missing boot image/loader only warns. Emulation type is inferred solely from image length.
