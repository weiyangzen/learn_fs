# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevhl7x.c

Brother HL-720/HL-730 GDI/HBP printer driver.

Key behavior:
- Defines `hl7x0` printer device.
- Sets margins based on PCL paper size helper despite not being a PCL printer.
- Sends PJL/HBP initialization and Brother command streams.
- Builds command buffers with blank-line runs, horizontal offsets, line delta/repeat command encoding, and page form-feed.
- Compression between lines is disabled unless `USE_POSSIBLY_FLAWED_COMPRESSION` is defined, due documented streaking artifacts.

Risks / notes:
- External command format is custom and fragile.
- Historical comments document real printer compatibility problems.
- Temporary buffer free call appears inconsistent with allocation size naming, worth checking if maintaining.
