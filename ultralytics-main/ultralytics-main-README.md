# Zebrafish morphology and cardiac analysis

Code and data accompanying **High-Throughput Hazard Identification Reveals Cardiac and Developmental Toxicity of Liquid Crystal Monomers towards Zebrafish**.

- **Figures 5b and 6b:** [heatmap reproduction](Fig5b-6b-R-clustering%20heatmap/README.md) takes the supplied standardized matrices as input. No YOLO weights or training are needed.
- **Image and video analysis:** `ultralytics-main/` contains the bundled YOLOv8 source, training and evaluation scripts, and morphology and cardiac measurement code.
- **Annotations:** [Zebrafish dataset](https://huggingface.co/datasets/w5774/zebrafish).

## Python environment

The manuscript reports PyTorch 2.4.1, CUDA 12.1 and an NVIDIA GeForce RTX 4090D for training. The bundled Ultralytics source identifies itself as version 8.0.201. The commands below specify a suggested Windows setup; they do not reconstruct unrecorded versions from the original training environment.

From the repository root, in PowerShell:

```powershell
cd ultralytics-main
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install torch==2.4.1 torchvision==0.19.1 --index-url https://download.pytorch.org/whl/cu121
python -m pip install -r requirements-zebrafish.txt
python -m pip check
python -c "import ultralytics; print(ultralytics.__version__, ultralytics.__file__)"
python -m pip freeze --all > environment-installed.txt
```

The requirements use NumPy 1.26.4 and `opencv-contrib-python` 4.10.0.84 as compatibility choices. The latter provides `cv2.ximgproc.thinning` for body-length measurements. Install only one OpenCV distribution in this environment.

## Prepare data and checkpoints

Use a separate YOLO segmentation YAML for each task. Match images with their label files by basename. Each label row is `class_id x1 y1 x2 y2 ...`, with polygon coordinates normalized to the image dimensions.

For a YAML located in `data/organ/dataset.yaml`, put `images/train`, `images/val`, and `images/test` beside it, with matching `labels/` subdirectories. Use those relative paths as the YAML entries, omit the optional `path` field, and set `names` to the verified class-ID mapping. The scripts pass the resolved YAML filename to the bundled loader.

**Check the class order and data split before evaluation.** The legacy example YAML and morphology script use different orders for `heart` and `yolk`. Use the mapping that matches the checkpoint and labels; check that the organ named `heart` corresponds to the pericardial region in the manuscript. The original public organ archive contains augmented derivatives of the same source images across subsets. For independent evaluation, use the actual source-disjoint split for the reported experiment and keep the file lists. Changing `split` to `test` does not resolve source overlap.

The scripts require trained `.pt` files, which must be supplied separately. Use the exact checkpoints for the analysis being reproduced. The curvature classifier is loaded from `weights_new/curve_classifier.pkl`; use the supplied, trusted copy.

## Run the project entry points

Run these commands from `ultralytics-main/`. Relative arguments are resolved from that directory, not from a machine-specific drive.

```powershell
# Train from the intended initialization checkpoint and dataset configuration.
python my_train.py --init-weights weights/init-seg.pt --data data/organ/dataset.yaml

# Export predictions from a trained checkpoint.
python my_predict.py --weights weights/organ.pt --source data/inference

# Evaluate the designated test subset; use --split val for validation.
python evaluation.py --weights weights/organ.pt --data data/organ/dataset.yaml --split test
```

The training entry point retains the settings in the original script (100 epochs, batch size 2, initial learning rate 0.01, and 0 workers). These are script defaults; use the recorded settings if they differ for a particular trained model. Pass `--compare` to evaluation to also export per-image box and mask comparisons, and body-length comparisons for the `body` class.

| Analysis | Inputs relative to `ultralytics-main/` | Command | Output |
| --- | --- | --- | --- |
| Morphology | `data/morphology/`; `weights_new/organ.pt`, `weights_new/body.pt`, `weights_new/curve_classifier.pkl` | `python organ/savemask.py` | `outputs/morphology/`: masks and `data.xlsx` |
| Cardiac video | `data/videos/`; `weights/AT.pt`, `weights/VE.pt` | `python heart/heart_predict.py` | `outputs/cardiac_video/`: per-frame predictions and per-video workbooks |
| Fluorescence rhythm | `data/rhythm/`: XLSX workbooks with `Average Intensity` and `Elapsed Time` | `python heart/hr_data.py` | `outputs/rhythm/`: processed copies of the workbooks |

For the morphology and cardiac video commands, set `$env:PYTHONPATH = (Get-Location).Path` first so the scripts import the bundled Ultralytics source. Check spatial calibration against the acquisition resolution and resizing used for the measurements. The rhythm indices are derived from fluorescence signals and are surrogate measures.

The optional offline augmentation entry point is `Augumentation/test.py`. Run it in a separate environment with `numpy==1.26.4`, `imgaug==0.4.0`, `opencv-python==4.10.0.84`, and `imageio`. It reads JPG images and LabelMe JSON files from `Augumentation/images/` and `Augumentation/labels/`, and writes derivatives to `Augumentation/output/`. Keep derivatives of a given source within its assigned subset.

The bundled Ultralytics license is in `ultralytics-main/LICENSE`. Cite the associated study when using its data or workflow.
