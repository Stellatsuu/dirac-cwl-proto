%YAML 1.1
---
cwlVersion: v1.2
class: CommandLineTool
baseCommand:
  - ctapipe-optimize-event-selection
  - --log-level=INFO
doc: |
  Optimize the signal/background event cuts given simulated input data.
  (DPPS-UC-130-1.9)
label: Optimize event selection
inputs:
  config:
    type: File?
    inputBinding:
      prefix: --config
    doc: |
      Sets the parameters for the ctapipe-optimize-event-selection tool.

  gammas:
    type: File
    doc: |
      path to input file containing pre-processed gamma-ray signal events.
    inputBinding:
      prefix: --gamma-file

  protons:
    type: File
    doc: |
      path to input file containing pre-processed proton background events.
    inputBinding:
      prefix: --proton-file

  electrons:
    type: File
    doc: |
      path to input file containing pre-processed electron background events.
    inputBinding:
      prefix: --electron-file

  output_filename:
    type: string
    doc: |
      Output FITS file where CUTS will be written. Note .fits.gz files fail, use
      just .fits as the extension.
    default: "event_selection.fits" # note gzipped files currently fail
    inputBinding:
      prefix: --output

  provenance_log_filename:
    type: string
    doc: file in which to write the local provenance.
    default: optimize_event_selection.provenance.log
    inputBinding:
      prefix: --provenance-log

outputs:
  event_selection:
    type: File
    doc: FITS format output file.
    format: fits
    outputBinding:
      glob: $(inputs.output_filename)
  provenance_log:
    type: File
    doc: ctapipe format provenance log for this step.
    outputBinding:
      glob: $(inputs.provenance_log_filename)
