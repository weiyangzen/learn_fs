# sources/security-integrity/ecryptfs-utils/doc/design_doc/Makefile.am

Purpose: builds and packages the eCryptfs design document.

Important APIs/targets: tracks TeX sources, diagrams, EPS files, generated TOC, final directory, and tarball. `final-hook`, PDF/PS/DVI/HTML targets, and clean rules mirror the beginner guide but with stricter commands in some recipes.

Control flow/state: generated PDF and HTML are copied into `final`; optional install controlled by `BUILD_DOCS`, regeneration by `BUILD_DOCS_GEN`.

Dependencies/integration: relies on LaTeX, DVIPS, PS2PDF, latex2html, and tar from configure.

Risks: diagram sources and generated EPS/HTML/PDF can drift. Unlike the beginner guide, some commands are not ignored, so docs-gen failures may stop builds.

Test signals: docs-gen and dist build validate this file.
