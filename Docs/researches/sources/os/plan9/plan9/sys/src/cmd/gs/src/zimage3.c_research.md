# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zimage3.c

LanguageLevel 3 ImageType 3 and ImageType 4 support for masked images. It registers `.image3` and `.image4`.

`zimage3` reads an image dictionary with `InterleaveType`, `DataDict`, and `MaskDict`. It parses the data image with `pixel_image_params`, parses the mask image with `data_image_params`, verifies both nested dictionaries declare `ImageType 1`, and enforces the InterleaveType/DataSource rules: mask data source is required exactly for InterleaveType 3, data multiple sources are only allowed with InterleaveType 3, and mask multiple sources are rejected. For InterleaveType 3 it inserts the mask source before data sources before calling `zimage_setup`.

`zimage4` handles color-key masking. It parses a normal pixel image, reads `MaskColor`, supports either exact component values or component ranges, clamps negative values into unsigned/no-match conventions, and then delegates to `zimage_setup`. Both operators reuse the incremental image engine from `zimage.c`.
