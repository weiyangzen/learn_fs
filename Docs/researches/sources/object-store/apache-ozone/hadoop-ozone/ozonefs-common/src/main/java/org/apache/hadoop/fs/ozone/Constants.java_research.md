<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/Constants.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/Constants.java

## Purpose
Small constants holder for Ozone filesystem implementation defaults and configuration keys shared across compatibility modules.

## Important APIs, types, and functions
It defines `OZONE_DEFAULT_USER`, `OZONE_USER_DIR`, `BUFFER_DIR_KEY`, `BUFFER_TMP_KEY`, and `LISTING_PAGE_SIZE`. The private constructor prevents instantiation.

## Control flow
There is no runtime control flow. Consumers statically import or reference constants.

## State and persistence behavior
No state is stored. Constants influence working-directory defaults and buffer/listing behavior elsewhere.

## Dependencies and integration points
`BasicRootedOzoneFileSystem` uses the default user and `/user` root when initializing home/working directories. Other Ozone FS code may use buffer keys for local temporary write buffering.

## Risks and test signals
Changing constant values can alter default home directories or listing/buffer defaults globally. Tests that assert working directory, home directory, and default listing behavior would catch accidental contract changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/Constants.java -->
