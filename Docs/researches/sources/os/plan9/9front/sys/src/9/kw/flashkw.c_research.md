# File Research: sources/os/plan9/9front/sys/src/9/kw/flashkw.c

SheevaPlug/Kirkwood NAND flash driver for the glueless NAND interface, focused on Hynix/Samsung large-page NAND chips. It maps the command/address/data registers through address bit aliases and implements the Plan 9 flash interface.

The driver probes NAND by resetting the chip, polling status, reading ID bytes, matching vendor/device IDs, and deriving page, erase-block, and spare sizes from the ID fields. It supports block erase, page read, page write, and unaligned read/write by read-modify-write of whole pages.

ECC is software based using `nandecc` and `nandecccorrect`, computed per 256-byte chunk and stored in the last 24 spare bytes for a 2 KiB page. Reads validate and correct one-bit data/ECC errors; uncorrectable ECC errors fail the read. A single-page cache avoids repeated NAND reads and supports partial-page rewrites.

Hardware access is serialized with `nandclaim`/`nandunclaim`, which toggles the NAND chip-enable control bit. `ctlrwait` polls status and resets the flash if it appears stuck.

Notable risks: comments say this should eventually merge with the generic NAND code; erase invalidates the whole single-page cache; write support is page-granular internally and assumes spare area is large enough for the ECC layout.
