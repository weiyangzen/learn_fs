# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/fwdownload.c

## Purpose
Implements firmware download for SCSI and ATA devices, using SCSI WRITE BUFFER or ATA DOWNLOAD MICROCODE as appropriate.

## Main Elements
- Vendor table encodes vendor/device matching, packet sizes, WRITE BUFFER mode bytes, offset/buffer ID behavior, readiness requirements, and timeout strategy.
- `fw_get_vendor()`: matches SCSI inquiry vendor or ATA identify model to vendor table.
- `fw_get_timeout()`: honors user timeout or probes REPORT SUPPORTED OPERATION CODES timeout descriptors for WRITE BUFFER.
- `fw_validate_ibm()`: validates IBM tape firmware file header against device VPD page 0x03.
- `fw_read_img()`: opens and reads firmware image, skipping known vendor-specific headers and validating special IBM tape images.
- `fw_check_device_ready()`: tests SCSI readiness or ATA identify response according to vendor policy.
- `fw_rescan_target()`: sends `XPT_SCAN_TGT` via `/dev/xpt` after successful download.
- `fw_download_img()`: chunks firmware, draws progress, and sends SCSI WRITE BUFFER or ATA DOWNLOAD MICROCODE commands; supports simulation mode.
- `fwdownload()`: parses `-f`, `-q`, `-s`, `-y`; identifies device; prompts unless confirmed; runs download.

## Dependencies And Integration
Uses CAM, SCSI inquiry/opcode helpers, ATA identify helpers, `progress.c`, and shared confirmation/transfer-rate functions.

## Risk Notes
Explicitly warns that firmware download may damage drives. The command has confirmation, simulation mode, vendor checks, readiness checks, and timeout probing, but the core path still writes firmware to hardware.
