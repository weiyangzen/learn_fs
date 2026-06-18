<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/tcmalloc_install_or_build.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/tcmalloc_install_or_build.sh

Purpose: makes MongoDB's patched TCMalloc shared library available for preloading in Evergreen builds, preferring S3 prebuilt artifacts and building/uploading when missing.

Control flow: requires build variant, defines patched source tag `mongo-20240522`, reads S3 and AWS credential expansions, tries `aws s3 cp --quiet` for `tcmalloc-<tag>-<variant>.tgz`, and extracts on success. If the object is missing, it downloads bazelisk for current OS/arch, sets Bazel 7.5.0, downloads the patched tcmalloc source, writes a Bazel `cc_shared_library` BUILD file, builds `libtcmalloc.so`, packages it under `TCMALLOC_LIB`, uploads to S3, and exits using the local build.

State and persistence: writes bazelisk, tarballs, source dir, `TCMALLOC_LIB`, and S3 object.

Dependencies and integration: called by Evergreen configure when `ENABLE_TCMALLOC=1`; `PREPARE_TEST_ENV` later uses `LD_PRELOAD`.

Risks and test signals: AWS download exit code `1` is treated as expected missing artifact; other codes fail. Build path is unsupported on Windows. Upload failure fails the WT build even though a local library exists, intentionally surfacing cache problems.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/tcmalloc_install_or_build.sh -->
