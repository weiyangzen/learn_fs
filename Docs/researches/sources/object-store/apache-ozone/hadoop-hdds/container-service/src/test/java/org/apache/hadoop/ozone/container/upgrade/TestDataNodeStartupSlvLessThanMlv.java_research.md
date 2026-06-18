## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/upgrade/TestDataNodeStartupSlvLessThanMlv.java

Purpose: Tests datanode startup rejection when stored metadata layout version exceeds the software layout version.

Important APIs/types/functions: `DatanodeStateMachine`, `DatanodeLayoutVersion` directory constant `DATANODE_LAYOUT_VERSION_DIR`, `HDDSLayoutVersionManager.maxLayoutVersion`, `UpgradeTestUtils.createVersionFile`, and `DatanodeDetails`.

Control flow: Creates metadata layout directory under a temp folder, configures `OZONE_METADATA_DIRS`, writes a VERSION file with MLV = max SLV + 1, constructs `DatanodeStateMachine`, and asserts `IOException` message ends with the expected MLV > SLV text.

State and persistence behavior: Writes a real VERSION file in a temp metadata directory.

Dependencies and integration points: Guards upgrade layout storage compatibility at datanode startup.

Risks and test signals: Strong safety signal for downgrade/incompatible metadata detection. Message suffix assertion couples to exception text.
