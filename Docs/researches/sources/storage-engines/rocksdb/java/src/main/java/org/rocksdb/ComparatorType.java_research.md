# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ComparatorType.java

Purpose: enum distinguishing comparator callback implementation strategy: byte-array comparator or direct-buffer comparator.

Control flow is a small immutable byte mapping with package-visible `getValue()`. It has no reverse lookup and is consumed by comparator/native binding code. State is not persisted by Java except as a native option/config value where applicable. Dependencies are minimal and sit in the comparator integration area.

Risks: byte drift with native comparator type constants would select the wrong callback ABI. Tests should verify the byte values indirectly through comparator construction, one byte-array comparator path, and one direct-buffer comparator path.
