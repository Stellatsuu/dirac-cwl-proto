%YAML 1.1
---
cwlVersion: v1.2
class: Workflow
label: Optimize cuts and Generate IRF
doc: |
  Optimize event selection and compute an IRF using the results.
requirements:
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}

inputs:
  optimize_config:
    type: File?
    doc: |
      Sets the parameters for the ctapipe-optimize-event-selection tool.

  irf_config:
    type: File?
    doc: |
      Sets the parameters for the IRF tool.

  gammas_optimize:
    type: File
    doc: |
      path to input file containing pre-processed gamma-ray signal events to use
      for optimization (should be independent of those use for IRF computation)

  protons_optimize:
    type: File
    doc: |
      path to input file containing pre-processed proton background events to use
      for optimization (should be independent of those use for IRF computation).

  electrons_optimize:
    type: File
    doc: |
      path to input file containing pre-processed electron background events to use
      for optimization (should be independent of those use for IRF computation).

  gammas_irf:
    type: File
    doc: |
      path to input file containing pre-processed gamma-ray signal events to use
      for IRF generation (should be independent of those use for optimization).

  protons_irf:
    type: File
    doc: |
      path to input file containing pre-processed proton background events to use
      for IRF generation (should be independent of those use for optimization).

  electrons_irf:
    type: File
    doc: |
      path to input file containing pre-processed electron background events to use
      for IRF generation (should be independent of those use for optimization).


  analysis_name:
    type: string
    doc: |
      Base name, e.g the name of the data processing or instrument configuration
      used for the input files. It will be used to generate the filenames of the
      output IRFs, metrics, and event selection files. e.g "ctao-north", will
      result in "ctao-north.irf.fits", "ctao-north.performance.fits",
      "ctao-north.event_selection.fits"

outputs:
  event_selection:
    type: File
    format: fits
    doc: event-selection file in FITS format.
    outputSource: optimize_irf/event_selection
  irf:
    type: File
    doc: Instrumental Response Function stored in a FITS file.
    format: fits
    outputSource: compute_irf/irf
  metrics:
    type: File
    doc: Performance metrics for the IRF in FITS format.
    outputSource: compute_irf/metrics
  optimize_provenance_log:
    type: File
    outputSource: optimize_irf/provenance_log
  compute_irf_provenance_log:
    type: File
    outputSource: compute_irf/provenance_log

steps:
  optimize_irf:
    run: optimize.cwl
    in:
      analysis_name: analysis_name
      config: optimize_config
      gammas: gammas_optimize
      protons: protons_optimize
      electrons: electrons_optimize
      output_filename:
        valueFrom: $(inputs.analysis_name + ".event_selection.fits")
    out:
      - event_selection
      - provenance_log
  compute_irf:
    run: compute_irf.cwl
    in:
      analysis_name: analysis_name
      config: irf_config
      gammas: gammas_irf
      protons: protons_irf
      electrons: electrons_irf
      event_selection: optimize_irf/event_selection
      output_filename:
        valueFrom: $(inputs.analysis_name + ".irf.fits")
      output_metrics_filename:
        valueFrom: $(inputs.analysis_name + ".performance.fits")
    out:
      - irf
      - metrics
      - provenance_log
