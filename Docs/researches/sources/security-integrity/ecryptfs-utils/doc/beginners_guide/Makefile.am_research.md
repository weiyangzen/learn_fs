# sources/security-integrity/ecryptfs-utils/doc/beginners_guide/Makefile.am

Purpose: builds, packages, and optionally installs the eCryptfs beginner guide.

Important APIs/targets: `FILENAME=ecryptfs_beginners_guide`; `final-hook` creates a `final` directory containing HTML assets and PDF; tarball hook packages it; `BUILD_DOCS` installs `final/*`; `BUILD_DOCS_GEN` enables regeneration and clean rules.

Control flow/state: LaTeX produces DVI, DVIPS produces PS, PS2PDF produces PDF, and latex2html produces HTML. Generated artifacts are included in distributions so users need not regenerate docs.

Dependencies/integration: configure supplies `TAR`, `PS2PDF`, `DVIPS`, `LATEX2HTML`, and `LATEX` when docs generation is enabled.

Risks: recipes prefixed with `-` ignore generation failures in several places, which may hide broken docs. Generated `final` content can become stale.

Test signals: docs generation, `make dist`, and package docs install.
