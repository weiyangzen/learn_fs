# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/imgtrans.c

This file dispatches image translation based on image metadata.

Key routine:
- `bTranslateImage(...)` validates the diagram/file/image state, checks image options, and dispatches to `bTranslateDIB`, `bTranslateJPEG`, `bTranslatePNG`, or `bAddDummyImage`.

Important behavior:
- Minimal-information images always become dummy placeholders.
- PNG translation is disabled for `level_ps_2` and becomes a dummy image.
- EMF, WMF, PICT, external, and unknown images currently become dummy placeholders.

Dependencies:
- Image examination output, conversion options, DIB/JPEG/PNG translators, dummy image renderer.

Role in antiword:
- Central image conversion router between image metadata and output-specific image rendering.
