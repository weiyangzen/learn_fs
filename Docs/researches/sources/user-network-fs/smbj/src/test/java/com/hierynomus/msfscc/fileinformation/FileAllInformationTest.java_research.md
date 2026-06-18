# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msfscc/fileinformation/FileAllInformationTest.java
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msfscc/fileinformation/FileAllInformationTest.java

Purpose: tests parsing or composition of `FileAllInformation`, the aggregate MS-FSCC file information structure. It verifies that substructures such as basic, standard, internal, EA, access, position, mode, alignment, name, and related fields are read with correct offsets.

State and persistence: transient byte buffers and model objects. Dependencies are MS-FSCC file information classes and JUnit. Integration point is SMB query-info responses. Risks covered include field ordering, padding, variable-length names, and substructure boundaries. Test signal is important because this aggregate structure is easy to misalign.
