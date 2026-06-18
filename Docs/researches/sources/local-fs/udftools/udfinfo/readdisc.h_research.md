# File Research: sources/local-fs/udftools/udfinfo/readdisc.h

## Role

Public header for the shared UDF reader.

## Contents

- Forward-declares `struct udf_disc`.
- Declares `int read_disc(int, struct udf_disc *)`.

## Research Notes

This header is intentionally minimal so both `udfinfo` and `udflabel` can reuse the same disk-reading implementation.
