# File Research: sources/virtualization/nvme-cli/plugins/toshiba/toshiba-nvme.c

Implements Toshiba vendor commands for SMART/vendor logs, internal logs, and clearing PCIe correctable errors.

Vendor SCT command path:
- `nvme_sct_op()` sends admin passthrough commands.
- `nvme_get_sct_status()` validates status version and supported device code.
- Supported device masks currently map internal codes `0x0d` and `0x10`.

Internal log flow:
- Sends SCT command transfer with action code `0xfffb`.
- Function code `0x0001` selects current log; `0x0002` selects saved log.
- Reads SCT data transfer pages in chunks.
- Can dump to stdout or write to an output file with progress bar.
- Reads header page to infer total log sectors from three area last-page fields.

Vendor log flow:
- Supports log IDs `0xc0` and `0xca`.
- `0xc0` is decoded as a vendor log page directory.
- Other supported logs are hex-dumped or written to file.

Clear errors:
- Uses Set Features ID `0xca`, namespace all, value bit 0 set.

Risks/notes:
- Several pointer arithmetic operations are performed on `void *`, relying on compiler extension.
- `d_raw_to_fd()` write loop does not advance the buffer pointer after partial writes.
- Progress output is printed even when dumping to stdout in some paths.
