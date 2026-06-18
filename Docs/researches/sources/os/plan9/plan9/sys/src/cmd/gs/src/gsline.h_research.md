# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsline.h

Public header for line parameters and rendering-quality controls. It includes `gslparam.h` for line cap/join enums and declares all setter/getter functions implemented by `gsline.c`.

It separates standard PostScript-style parameters from Ghostscript extensions and also exposes imager-level accessors for flatness, dash adaptation, and accurate-curve settings through the opaque `gs_imager_state`.
