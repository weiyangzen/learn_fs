# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/scsireq.c

Purpose: Core SCSI request library used by scuzz and related tools.

Major functions:
- Basic commands: `SRready`, `SRrewind`, `SRreqsense`, `SRformat`, `SRrblimits`, `SRseek`, `SRfilemark`, `SRspace`, `SRinquiry`, mode select/sense, `SRstart`, `SRrcapacity`.
- I/O: `SRread` and `SRwrite` choose 6-byte or 10-byte direct-access commands, or sequential tape commands, validate block alignment, update offsets, and handle tape short reads/filemarks.
- Transport: `request` writes command bytes to `/dev/sdXX/raw`, transfers data, and reads status text.
- `SRrequest`: wraps transport, retries busy status, converts CHECK CONDITION into sense data, and supports USB through `umsrequest`.
- Open/close: `SRopenraw`, `SRopen`, `SRclose`; device-specific open helpers configure direct, sequential, WORM, printer, or changer devices.

Integration: Shared by `scuzz.c`, CD helpers, changer helpers, USB mass storage users, and `cdfs` per header comment.

Risks:
- Explicit comments note incomplete LUN support.
- Exabyte and forced 6-byte command flags alter behavior globally.
- Sequential-device short-record handling relies on sense fields.
- Raw device protocol expects Plan 9 `/dev/sdXX/raw` behavior: write CDB, transfer data, read status.
