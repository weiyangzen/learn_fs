# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/udf.h

## Purpose

`udf.h` is the local umbrella header for `udf_info` implementation files. It collects the platform layer and core UDFS internal interfaces used by the source files in this directory.

## Contents

The header includes:

- `Include/platform.h`
- `udffs.h`
- `namesup.h`

It defines no local declarations, macros, functions, or data of its own.

## Role in This Group

All implementation files in this group include `udf.h` directly. Through this header they receive Windows/kernel platform definitions, UDFS VCB/FCB structures, filesystem constants, helper macros, and name-support declarations.
