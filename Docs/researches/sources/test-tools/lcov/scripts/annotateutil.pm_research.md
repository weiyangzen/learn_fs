# sources/test-tools/lcov/scripts/annotateutil.pm

Purpose: shared support module for annotation and version callbacks. It provides common output formatting, mtime/md5 helpers, fallback annotation for files outside a repository, and a cache-aware `AnnotateBase` superclass used by git and Perforce annotators.

Important APIs/types: package `annotateutil` exports `get_modify_time`, `compute_md5`, `call_annotate`, and `call_get_version`. Package `AnnotateBase` exposes `new`, `printlog`, `resolve_cache_dir`, `find_in_cache`, `store_in_cache`, `verify_annotation`, and `annotate`; subclasses implement `annotate_callback`.

Control flow and state: `call_annotate` constructs the callback class, invokes `annotate`, and emits pipe-delimited `cl|abbrev;full|when|text` records. `AnnotateBase::annotate` first checks a Storable cache keyed by source path and validated against `lcovutil::extractFileVersion`; on miss it delegates to `annotate_callback`, falls back to filesystem ownership/mtime if undef, optionally verifies text, and stores cache data.

Dependencies and integration: uses `POSIX`, `Cwd`, `Fcntl`, `File::Path`, `File::Spec`, `File::Basename`, `Storable`, and many `lcovutil` globals/functions provided by callback host scripts. `gitblame.pm` and `p4annotate.pm` inherit from it.

Risks and test signals: `compute_md5` shells out with an unquoted filename. Cache correctness depends on a configured version callback unless version errors are ignored. `verify_annotation` compares chomped lines without CR stripping on local file reads, while annotators often strip CR. Tests exercising `--annotate-script`, `--cache`, `--verify`, and version mismatch handling provide coverage signals.
