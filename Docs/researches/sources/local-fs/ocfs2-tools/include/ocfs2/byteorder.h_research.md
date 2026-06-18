# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/byteorder.h

## Purpose

Defines endian conversion macros for OCFS2 userspace code.

## Main Contents

- Includes `<endian.h>`, `<byteswap.h>`, and `<stdint.h>`.
- Documents that OCFS2 on-disk fields are little-endian except JBD journal fields, which use their own big-endian format.
- For little-endian hosts, little-endian conversions are identity and big-endian conversions use byte swaps.
- For big-endian hosts, little-endian conversions use byte swaps and big-endian conversions are identity.
- Defines `cpu_is_little_endian` and `cpu_is_big_endian`.

## Dependencies and Integration

- Used throughout libocfs2 swapping code and disk structure handling.

## Research Notes

- The macros are guarded so existing platform definitions can override them.
- Build fails explicitly on unknown `__BYTE_ORDER`.
