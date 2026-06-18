# File Research: sources/teaching/minix/minix/drivers/storage/filter/crc.h

## Purpose
Declares the filter driver CRC helper.

## Contents
- Include guard `_CRC_H`.
- Prototype: `compute_crc(const unsigned char *b, size_t n)`.

## Integration Notes
Included by `sum.c`.

## Risks
The header assumes `size_t` is already declared by prior includes.
