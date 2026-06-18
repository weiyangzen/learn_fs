# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/barkmel.c

## Role

This is a small diagnostic utility for printing Bark-scale frequency mappings for common Vorbis block sizes and sample rates.

## Behavior

`main()` iterates block sizes from 64 to below 32000 and prints, for sample rates from 48 kHz down to 8 kHz:

- Frequency represented by bin 1.
- Bark value for that bin.
- Bark value for Nyquist.

It also prints Bark-to-Hz mappings for integer Bark values 0 through 27, including approximate bin positions for a 128-bin 44.1 kHz half-spectrum.

## Dependencies

It includes `scales.h` and uses `toBARK()` and `fromBARK()`.

## Integration Notes

This is not part of normal codec runtime. It is a development/analysis helper.
