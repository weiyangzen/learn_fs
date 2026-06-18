<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/perf_test/resnet50_classify.py -->
# sources/user-network-fs/blobfuse2/test/perf_test/resnet50_classify.py

Source path: `sources/user-network-fs/blobfuse2/test/perf_test/resnet50_classify.py`

## Purpose
TensorFlow ResNet50 image classification workload for measuring mounted-image read performance.

## Important APIs, Types, And Functions
Functions: `classify_images`, `chunks`. Classes: none declared. Imports: `os`, `sys`, `time`, `json`, `argparse`, `numpy`, `multiprocessing.*`, `tensorflow.keras.applications.*`, `tensorflow.keras.preprocessing.image.*`, `tensorflow.keras.preprocessing.image.*`, `tensorflow.keras.applications.imagenet_utils.*`.

## Control Flow
Parses arguments, partitions image files into chunks, uses multiprocessing workers to load/preprocess images, runs ResNet50 classification, and records timing/summary output.

## State And Persistence
Reads images from the target path and writes timing/report JSON or stdout summaries; model weights may be cached by TensorFlow/Keras.

## Dependencies And Integration Points
Integrates with Python runtime packages, benchmark datasets, mounted filesystem paths, and JSON/Parquet/report artifacts used by blobfuse2 performance experiments.

## Risks
Requires TensorFlow, NumPy, enough memory, and model download/cache availability. GPU/CPU differences and image cache effects can dominate filesystem measurements.

## Test Signals
Signals are successful script exit, valid generated JSON/Parquet/report files, timing metrics, and absence of unexpected read/classification/data-generation exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/perf_test/resnet50_classify.py -->
