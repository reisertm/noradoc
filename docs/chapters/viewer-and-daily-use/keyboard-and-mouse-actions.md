# Keyboard And Mouse Actions

This chapter summarizes keyboard shortcuts and mouse actions in NORA, grouped by where they apply. Generic HTML behaviors such as pressing `Enter` in simple form fields are not listed here.

## Viewer keyboard shortcuts

- `F5`
  Reload the page, but first run NORA's unsaved-changes check.
- `Ctrl+R` or `Cmd+R`
  Reload the page, but first run NORA's unsaved-changes check.
- `X`
  Step one slice in the positive direction in the currently hovered active 2D viewport.
- `Y` or `Z`
  Step one slice in the negative direction in the active 2D viewport. The code supports both to cover `QWERTZ` and `QWERTY` layouts.
- `Shift+X`
  Increase the global slice scroll speed.
- `Shift+Y`
  Decrease the global slice scroll speed.
- `0` to `8`
  Apply a configured color-limit or windowing preset to all loaded medical viewers, if a preset exists for that key in `colormap.colorlimpresets`.
- `Space`
  Toggle drawing on the current ROI, if the ROI tool is active.
- `Esc`
  Clear the current ROI drawing target and also close open dialogs or menus such as the command dialog, grid jobs dialog, settings dialog, user settings dialog, and patient-table context menu.
- `V`
  Temporarily hide all currently visible ROIs, and restore them when pressed again.
- `N`
  If TFJS segmentation is available through the ROI tool:
  Tap `N` to run segmentation on the current slice.
  Hold `N`, move to another slice, and release to segment the inclusive slice range between press and release.
  Press `N` again while segmentation is running to request stop.
- `R`
  Reset the crosshair position. In the current code path, plain `R` also opens the rights section of the settings dialog.
- `C`
  Centralize the current view around the crosshair.
- `S`
  Open the settings dialog.
- `B`
  Toggle the command or batch dialog.
- `G`
  Toggle the grid jobs dialog.
- `Shift+C`
  Open the settings dialog and jump to `projectManagement -> clin_info`.
- `Shift+P`
  Run `addWorkstatePostCode()`.
- `M`
  Trigger the segmentation `"memorize"` action through the ROI tool.
- `Up` or `Down`
  If autoloaders are enabled, move to the previous or next row or case in the patient table.
- `Ctrl+S`
  When the command dialog is visible, save the active entry.
- `Ctrl+D`
  When the grid jobs dialog is visible, clear dead jobs.

## Reading workflow keyboard shortcuts

These shortcuts are active while the Reading Tool is enabled and a reading is active.

- `Alt+N`
  Jump to the next unrated case.
- `Up`
  Go to the previous case.
- `Down`
  Go to the next case.
- `Enter`
  Go to the next unrated case.
- `Space`
  Go to the next unrated case.
- `0` to `9`
  Toggle or advance the matching reading form item by shortcut number.
- `Numpad 0` to `Numpad 9`
  Also toggle the matching reading form item.
- `Shift+number`, `Ctrl+number`, or `CapsLock+number`
  Add `10` to the shortcut number, so the same key family can address higher-numbered form items.

## ROI and segmentation keyboard shortcuts

- `Ctrl+Z`
  Undo ROI history.
- `Ctrl+Shift+Z`
  Redo ROI history.
- `W`
  Run remote segmentation for the ROI workflow via `runRemoteSegment("roi")`.

## 3D object and fiber keyboard shortcuts

- `Ctrl+Z`
  Undo fiber or object history in the 3D object tool.
- `Ctrl+Shift+Z`
  Redo fiber or object history in the 3D object tool.

## 2D viewer mouse actions

- `Mouse wheel`
  Change slice.
- `Ctrl + mouse wheel`
  Zoom the active 2D viewport.
- `Ctrl + mouse wheel` in mosaic mode
  Zoom the mosaic crop region around the current crosshair position.
- `Ctrl + mouse wheel` with an active scribble marker set in `createonclick` mode
  Change the scribble pen radius.
- `Shift + mouse wheel` with an active current ROI
  Change ROI pen size.
- `Shift + mouse wheel` in mosaic mode
  Change the mosaic column count.
- `Shift + mouse wheel` on 4D data outside ROI drawing mode
  Change time point.
- `Left click`
  Move the world position or crosshair to the clicked point.
- `Left drag`
  Move the crosshair continuously.
- `Ctrl + left drag`
  Pan or reformat synchronized viewports through the shared zoom limits.
- `Shift + left drag`
  Pan only the current viewport.
- `Ctrl + Shift + left click` on 4D data
  Create a time-series pin viewer at the clicked point.
- `Ctrl + Shift + left drag` on 4D data
  Keep showing the time-series pin viewer while dragging.
- `Middle drag`
  Adjust image windowing or color limits.
- `Right drag`
  Pan the current viewport.
- `Shift + right drag`
  Pan synchronized world-locked viewports when global coordinates are active. If synchronization is not active, it behaves like local panning.
- `Right drag` in mosaic mode
  Move the mosaic crop box.
- `Alt + drag` while ROI pen mode is active
  Change ROI pen radius.
- `Left drag` while an ROI is the current drawing target
  Paint the ROI.
- `Right drag` while an ROI is the current drawing target
  Erase or modify the ROI using the current ROI tool mode.
- `Ctrl + right click` with an ROI
  Open the ROI context picker.
- `Right click` without a current ROI
  Attempt ROI context picking or ROI-based context analysis at the clicked point.
- `Hold Ctrl while the mouse is over a 2D viewport`
  Reveal the central crosshair handle. In scribble marker mode, this instead enables scribble modification mode.

## 3D viewer mouse and modifier actions

- `Left drag`
  Rotate the 3D camera.
- `Right drag`
  Pan the 3D camera.
- `Ctrl + mouse wheel`
  Zoom the 3D camera by changing camera radius.
- `Mouse wheel` over a picked slice plane in 3D
  Move the corresponding slice.
- `Shift + mouse wheel` over a marker point in 3D
  Change marker size.
- `Shift + mouse wheel` with an active ROI in 3D
  Change ROI pen radius.
- `Shift + mouse wheel` in a fiber view
  Change the fiber selection radius.
- `Shift + click or drag` with a current ROI in 3D
  Paint or modify the ROI in 3D.
- `Shift + left click` in marker `createonclick` mode
  Add a marker point.
- `Shift + right click` in marker `createonclick` mode
  Delete the clicked marker point.
- `Shift + click or drag` on fibers
  Select fibers.
- `Ctrl + Shift + click or drag` on fibers
  Append fibers to the current fiber selection.
- `Alt + Shift + click or drag` on fibers
  Subselect fibers.
- `Shift + right click` on fibers
  Delete fibers from the selection.
- `Ctrl + drag` on a slice plane or plane controller in 3D
  Drag the slice plane through the volume.
- `Right click` on a 3D object with a context menu
  Open the object-specific context menu.
- `Hold Shift while hovering in 3D`
  Show and update the 3D ROI or fiber pencil under the cursor.
- `Hold Ctrl while hovering in 3D`
  Enable picking on large meshes and show 3D hover info.
- `Touch pinch`
  Zoom the 3D camera.

## Table and browser mouse actions

- `Release Shift` while the mouse is stationary over a patient, study, or file cell
  Open the patient-table context menu.
- `Ctrl + click` on deselectable analysis-table rows
  Toggle row exclusion.
- `Ctrl + Shift + click` on deselectable analysis-table rows
  Toggle exclusion over a row range.
- `Ctrl + click` on analysis-table headers
  Toggle or cycle column selection state.
- `Shift + click` on analysis-table headers
  Mark a column using the alternate selection state.

## Notes

- Many shortcuts only work when focus is on `document.body`, which means they do not fire while typing in an input field, textarea, or editable element.
- Several actions are mode-dependent. For example, the same mouse gesture can mean slice navigation, ROI painting, marker editing, or fiber selection depending on the active tool and current object.
- A few shortcuts in the current code overlap. The clearest example is plain `R`, which both resets the crosshair and opens the rights settings view.
