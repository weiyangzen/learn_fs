# sources/test-tools/cthon04/general/nroff.in

Purpose: static nroff/troff input fixture used by the general tests to exercise text processing over a realistic document.

Important APIs/types/functions: not executable code. It uses troff requests/macros such as .DA, .ds, .nr, .ps, .vs, .TL, .AU, .LP, .TS/.TE tables, .IP lists, and .SH sections.

Control flow: when processed by nroff/troff, the document defines headers/footers and typesetting parameters, emits a title/author, two tables, narrative paragraphs, conclusions, and future-work sections.

State and persistence behavior: read-only fixture; generated output is produced by whatever harness command processes it, not by this file itself.

Dependencies and integration points: consumed by general test scripts that run nroff or equivalent text-formatting tools; provides enough content and table markup to exercise parser and filesystem read paths.

Risks: content is historical sample prose with old spelling and performance data; tests depend on availability and behavior of legacy nroff/troff tools.

Test signals: successful formatter execution and expected output/timing files in the surrounding harness.
