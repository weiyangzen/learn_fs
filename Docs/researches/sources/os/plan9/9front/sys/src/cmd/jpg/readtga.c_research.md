# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readtga.c

TGA decoder for uncompressed and RLE color-mapped, RGB, and grayscale images. It parses the 18-byte TGA header, optional ID field, color-map origin/length, and converts color maps from BGR/BGRA or 15/16-bit packed form.

Pixel readers cover color-map indices, luma, luma RLE, RGB(A), and RGB(A) RLE for 15/16/24/32 bpp. Output channel descriptors include `CY`, `CRGB1`, `CRGBV`, `CRGB`, and `CRGBA`.

After decoding it applies horizontal reflection and vertical flip based on descriptor origin bits. It ignores alpha for most tool-level display paths, matching the file comment that TGA alpha is largely ignored.
