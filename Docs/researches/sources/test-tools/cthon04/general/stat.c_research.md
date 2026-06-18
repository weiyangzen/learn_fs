# sources/test-tools/cthon04/general/stat.c

Purpose: summarizer for timing output files produced by general tests.

Important APIs/types/functions: globals real/user/sys arrays with MAXINDEX=100, Prog, File; functions main(), getattfmt(), and prtstat(). Uses fopen(), fgetc(), ungetc(), fscanf(), fgets(), sscanf(), sqrt(), and printf().

Control flow: opens a datafile, skips non-data leading lines, detects BSD one-line time format or ATT multi-line format, parses up to MAXINDEX samples into arrays, then prints average and sample standard deviation for real/user/sys.

State and persistence behavior: read-only over the input file; stores parsed samples in process-global arrays and writes one summary line to stdout.

Dependencies and integration points: linked with libm; used by general test reporting to normalize timing files across Unix variants.

Risks: no bounds check in the BSD fscanf loop, so more than 100 samples overflows arrays; uses isdigit without including ctype.h; ATT parser assumes strict real/user/sys grouping.

Test signals: success prints three tab-separated average/stddev groups labeled real/user/sys; bad or empty input exits nonzero except SVR3 no-data compatibility.
