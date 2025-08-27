%YAML 1.1
---
cwlVersion: v1.2
class: CommandLineTool
baseCommand: ctapipe-compute-irf
doc: |
  Compute IRF and IRF metrics from pre-processed events and event selection
  cuts. (DPPS-UC-130-1.6)
label: Compute IRF
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

  event_selection:
    type: File
    doc: FITS file containing optimized cuts to apply
    default: event_selection.fits
    inputBinding:
      prefix: --cuts

  output_filename:
    type: string
    doc: filename of output IRF file.
    default: irf.fits.gz
    inputBinding:
      prefix: --output

  output_metrics_filename:
    type: string
    doc: filename of output IRF benchmarks file.
    default: performance_metrics.fits.gz
    inputBinding:
      prefix: --benchmark-output

  provenance_log_filename:
    type: string
    doc: file in which to write the local provenance.
    default: compute_irf.provenance.log
    inputBinding:
      prefix: --provenance-log

outputs:
  irf:
    type: File
    doc: File containing computed IRF
    format: fits
    outputBinding:
      glob: $(inputs.output_filename)
  metrics:
    type: File
    doc: File containing IRF performance metrics
    format: fits
    outputBinding:
      glob: $(inputs.output_metrics_filename)
  provenance_log:
    type: File
    doc: ctapipe format provenance log for this step.
    outputBinding:
      glob: $(inputs.provenance_log_filename)
