# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sdcparam.h

Declares internal common DCT parameter routines used by DCT encode/decode parameter files. It exposes scalar get/put, quantization table get/put, Huffman table get/put, and byte-parameter extraction.

The header explicitly says these procedures are internal and not documented for general clients.

Dependencies include DCT stream state and Ghostscript parameter types supplied by including files.

This is JPEG parameter API glue.
