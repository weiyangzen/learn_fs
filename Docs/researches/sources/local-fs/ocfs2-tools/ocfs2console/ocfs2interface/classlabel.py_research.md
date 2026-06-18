# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/classlabel.py

Provides a descriptor that converts class names into human-readable labels.

Key contents:
- Regex `caps = re.compile('(?!\A)[A-Z][a-z]')`
- `make_title(m)`
  - Inserts a leading space before matched capitalized word segments.
- `class_label` descriptor
  - `__get__` returns transformed class name.
  - Example: `MaximumNodes` becomes `Maximum Nodes`.

Usage:
- Used by field classes in `general.py` and `ls.py` to auto-generate labels.

Notable details:
- Exports an instance named `class_label`, replacing the class name binding.
