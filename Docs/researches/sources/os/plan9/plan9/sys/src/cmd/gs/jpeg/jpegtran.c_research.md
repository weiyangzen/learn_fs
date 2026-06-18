# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jpegtran.c

Command-line JPEG transcoder. It reads JPEG input as DCT coefficients and writes JPEG output, optionally changing coding parameters and applying lossless or near-lossless coefficient-domain transforms.

The switch parser supports marker-copy policy, arithmetic coding, Huffman optimization, progressive output, scan scripts, restart intervals, max memory, output filename, verbosity, grayscale forcing, flips, rotations, transpose/transverse, and trimming non-transformable edge blocks. Transform selection rejects conflicting transform options.

`main()` creates separate decompression and compression objects, parses options once to find files and memory settings, opens input/output streams, sets the decompressor source, configures marker copying, reads the header, requests transform workspace, reads source coefficients, copies critical compression parameters, adjusts destination parameters for transforms, reparses options for final output settings, writes coefficient output, copies selected markers, executes the transform, finishes both JPEG objects, closes files, and exits with warning status if either JPEG object reported warnings.
