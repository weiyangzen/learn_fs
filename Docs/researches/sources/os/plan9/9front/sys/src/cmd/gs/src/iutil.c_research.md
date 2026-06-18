# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iutil.c

Provides general interpreter utilities for refs, strings, operands, packed arrays, operators, and matrices. It defines `ref_type_properties`, ref copy helpers with save/write barriers, null filling, equality and identity comparison, name/string data extraction, printable object conversion for `cvs`, `=`, `==`, and related operations, and operator index lookup/ref reconstruction.

Array helpers include `array_get`, `packed_get`, and `refs_check_space`, supporting ordinary, mixed, and short packed arrays. String helpers convert between C strings and Ghostscript string refs. Operand helpers extract numeric parameters, single real/float/int parameters, create real refs, and compute appropriate type/procedure check errors.

Matrix helpers read and write six-element matrices, including save-aware writes into existing arrays. The file intentionally avoids taking an interpreter context pointer and instead receives memory arguments directly where needed.
