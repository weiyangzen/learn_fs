# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gpmisc.h

Purpose: Declares shared platform utility functions implemented in `gpmisc.c`.

Key interfaces: `gp_gettmpdir`, `gp_fopentemp`, `gp_file_name_combine_generic`, `gp_file_name_reduce`, `gp_file_name_is_absolute`, `gp_file_name_parents`, and `gp_file_name_cwds`.

Integration: Included by platform files such as Unix-like and VMS implementations to share temporary-file and path-combining behavior.

Risks and notes: The header exposes `gp_file_name_combine_generic`, but comments explicitly direct platform-specific changes to the platform wrapper rather than the generic routine.
