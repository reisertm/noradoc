# LISP-Net: Clinician-Guided AI for Context-Aware Segmentation

**[Watch the demo video on YouTube](https://www.youtube.com/watch?v=SafGK6U0nDI)**

[LISP-Net repository](https://github.com/Machauer-P/lisp-net)

LISP-Net is a deep learning model that propagates a 2D ROI across distant slices using a single example as context. Given one annotated slice, it predicts the segmentation on other slices — adapting to your intention, anatomy, and style.

It feels natural: draw on one slice, then let the model carry your intent forward. Interact with the model if it comes off track.

Crucially, **LISP-Net runs entirely client-side in your browser** — powered by ONNX Runtime Web with WebGPU acceleration. No server, and no uploads. Your data never leaves your device.

## 1. Usage

LISP-Net is **keyboard-driven** — there is no menu or toolbar. All commands are single-key presses.

### Prerequisites

First, use the [ROI Tool](https://reisertm.github.io/noradoc/chapters/roi-tool.html) to draw a **single 2D ROI** on one slice.

---

### Step 1 — Memorize a Context Slice

With your ROI drawn on the reference slice, press **M**. The first time, LISP-Net loads the ONNX model into the browser (may take a few seconds), then immediately saves the current image and mask as the **prompt context** — the pair the model will use to understand and propagate your intent. A notification confirms when ready.

> The model needs only **one** annotated slice. On subsequent uses, pressing **M** simply updates the memorized context.

### Step 2 — Choose the Normalization Mode

Press **T** to toggle between **CT** and **MRI** normalization. This is critical for correct results:

| Mode  | Use for                                               |
|-------|-------------------------------------------------------|
| **CT**   | CT images (HU units). Applies fixed windowing: `[-1000, 1000]` clipped, shifted by `+15`, scaled by `1/160` |
| **MRI**  | MRI and everything else. Foreground percentile clipping (p0.5–p99.5) followed by per-volume z-score normalization |

The current mode is shown in a notification and persists across browser sessions.

### Step 3 — Predict on a Distant Slice

Scroll to any other slice and press **N**. LISP-Net predicts the segmentation on that slice using the memorized context. The result is written into your active ROI immediately.

### Batch Prediction — Hold N + Scroll

Hold down **N** and scroll through a range of slices. When you release **N**, LISP-Net will calculate predictions for every slice you passed through.

> Performance depends on image size, number of slices, and your hardware.

### Step 4 — Correct and Refine

If a prediction is not perfect:
1. Edit the ROI on that slice using the ROI tool
2. Press **M** again to save the corrected slice as a **new context**
3. Continue predicting on further slices

The model benefits from updated context — each correction improves subsequent predictions.

---

## 2. Expert Tips

### Feed Good Predictions as New Context

Even if a prediction is already good, you can press **M** on that slice to use it as fresh context. As you move further from the original slice, appearance may drift — updating context keeps the model aligned to the local anatomy.

### Switching Slicing Orientation

LISP-Net respects the current slicing dimension. If you switch between axial, coronal, or sagittal views, be aware that the memorized prompt was saved in a specific orientation. The model will warn you if you try to predict across slices in a different orientation.

### Cancelling

If a batch prediction is in progress and you want to stop it, press **N** again — the current run will be cancelled.

---

## 3. Keyboard Shortcuts Summary

| Key | Action |
|-----|--------|
| **M** | Memorize current slice as context (first press initializes the model if not loaded) |
| **N** | Predict on current slice (press & hold + scroll + release for batch prediction across a range) |
| **T** | Toggle CT / MRI normalization mode |
