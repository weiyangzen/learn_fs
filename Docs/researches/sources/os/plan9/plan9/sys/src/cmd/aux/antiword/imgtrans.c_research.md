# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/imgtrans.c

Generic image translation dispatcher.

Single public function:

- `bTranslateImage(diagram_type *pDiag, FILE *pFile, BOOL bMinimalInformation, ULONG ulFileOffsetImage, const imagedata_type *pImg)`

Behavior:

- If only minimal image information is available, adds a dummy image.
- DIB dispatches to `bTranslateDIB()`.
- JPEG dispatches to `bTranslateJPEG()`.
- PNG dispatches to `bTranslatePNG()` unless output image level is PS level 2, where it uses a dummy placeholder.
- EMF, WMF, PICT, external, unknown image types currently become dummy placeholders.

This file sits between `imgexam.c` and format-specific translators such as `dib2eps.c`, `jpeg2eps.c`, `png2eps.c`, or RISC OS sprite translators.
