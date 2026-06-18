<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/images.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/images.rs

## Purpose
This module exposes the image catalog endpoint for rcloud. It lists files in the configured base image directory and returns them as API model objects.

## Important APIs and Functions
`list_images(config)` receives Actix `web::Data<AppConfig>`, constructs `VmManager`, calls `manager.list_base_images()`, maps each image name into `ImageInfo`, and returns `ListImagesResponse`.

## Control Flow
The handler logs the request, performs a synchronous filesystem scan through `VmManager`, then branches on `Result`. Success returns HTTP 200 JSON. Failure logs the error and returns HTTP 500 with a JSON `error` string.

## State, Persistence, and Dependencies
The endpoint reads persistent base image files from `config.base_images_dir`; it does not mutate them. It depends on the VM manager implementation, Actix Web response types, Serde JSON, and tracing.

## Risks and Test Signals
The handler runs blocking filesystem work in an async handler, which is acceptable for small directories but can block Actix workers on slow storage. It exposes raw filenames rather than validated image metadata. Test signals should include a temporary base image directory and a missing-directory error path.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/images.rs -->
