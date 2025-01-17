# calibration_multi_frequency_through_propagation_measurement

**Goal**: Test the propagation response at multiple frequencies through interconnect cables. Use a through connection to measure the approximate propagation delay between identical cables.

## Experiment Parameters 

|    |   square_wave_frequency_Hz |
|---:|---------------------------:|
|  0 |                      1e+09 |
|  1 |                      3e+09 |
|  2 |                      5e+09 |
|  3 |                      1e+10 |

## Schema 
- **name**: calibration_multi_frequency_through_propagation_measurement
- **goal**: Test the propagation response at multiple frequencies through interconnect cables. Use a through connection to measure the approximate propagation delay between identical cables.
- **experiment_instances**:
  -
    - **name**: calibration_1000000000.0_Hz
    - **components**:
      -
        - **name**: two_port_oscilloscope
        - **ports**:
          -
            - **name**: CH1
            - **parent_component_name**: None
          -
            - **name**: CH2
            - **parent_component_name**: None
        - **connections**: None
        - **components**:
      -
        - **name**: two_port_oscilloscope
        - **ports**:
          -
            - **name**: CH1
            - **parent_component_name**: None
        - **connections**: None
        - **components**:
      -
        - **name**: power_splitter_1to2
        - **ports**:
          -
            - **name**: IN
            - **parent_component_name**: None
          -
            - **name**: OUT1
            - **parent_component_name**: None
          -
            - **name**: OUT2
            - **parent_component_name**: None
        - **connections**: None
        - **components**:
    - **connections**:
      -
        - **name**: None
        - **ports**:
          -
            - **name**: OUT1
            - **parent_component_name**: None
          -
            - **name**: CH1
            - **parent_component_name**: None
      -
        - **name**: None
        - **ports**:
          -
            - **name**: OUT2
            - **parent_component_name**: None
          -
            - **name**: CH2
            - **parent_component_name**: None
    - **goal**: 
    - **parameters**:
      - **square_wave_frequency_Hz**: 1000000000.0
    - **index**: None
    - **date_configured**: 
    - **date_measured**: 
    - **measurement_configuration_list**:
  -
    - **name**: calibration_3000000000.0_Hz
    - **components**:
      -
        - **name**: two_port_oscilloscope
        - **ports**:
          -
            - **name**: CH1
            - **parent_component_name**: None
          -
            - **name**: CH2
            - **parent_component_name**: None
        - **connections**: None
        - **components**:
      -
        - **name**: two_port_oscilloscope
        - **ports**:
          -
            - **name**: CH1
            - **parent_component_name**: None
        - **connections**: None
        - **components**:
      -
        - **name**: power_splitter_1to2
        - **ports**:
          -
            - **name**: IN
            - **parent_component_name**: None
          -
            - **name**: OUT1
            - **parent_component_name**: None
          -
            - **name**: OUT2
            - **parent_component_name**: None
        - **connections**: None
        - **components**:
    - **connections**:
      -
        - **name**: None
        - **ports**:
          -
            - **name**: OUT1
            - **parent_component_name**: None
          -
            - **name**: CH1
            - **parent_component_name**: None
      -
        - **name**: None
        - **ports**:
          -
            - **name**: OUT2
            - **parent_component_name**: None
          -
            - **name**: CH2
            - **parent_component_name**: None
    - **goal**: 
    - **parameters**:
      - **square_wave_frequency_Hz**: 3000000000.0
    - **index**: None
    - **date_configured**: 
    - **date_measured**: 
    - **measurement_configuration_list**:
  -
    - **name**: calibration_5000000000.0_Hz
    - **components**:
      -
        - **name**: two_port_oscilloscope
        - **ports**:
          -
            - **name**: CH1
            - **parent_component_name**: None
          -
            - **name**: CH2
            - **parent_component_name**: None
        - **connections**: None
        - **components**:
      -
        - **name**: two_port_oscilloscope
        - **ports**:
          -
            - **name**: CH1
            - **parent_component_name**: None
        - **connections**: None
        - **components**:
      -
        - **name**: power_splitter_1to2
        - **ports**:
          -
            - **name**: IN
            - **parent_component_name**: None
          -
            - **name**: OUT1
            - **parent_component_name**: None
          -
            - **name**: OUT2
            - **parent_component_name**: None
        - **connections**: None
        - **components**:
    - **connections**:
      -
        - **name**: None
        - **ports**:
          -
            - **name**: OUT1
            - **parent_component_name**: None
          -
            - **name**: CH1
            - **parent_component_name**: None
      -
        - **name**: None
        - **ports**:
          -
            - **name**: OUT2
            - **parent_component_name**: None
          -
            - **name**: CH2
            - **parent_component_name**: None
    - **goal**: 
    - **parameters**:
      - **square_wave_frequency_Hz**: 5000000000.0
    - **index**: None
    - **date_configured**: 
    - **date_measured**: 
    - **measurement_configuration_list**:
  -
    - **name**: calibration_10000000000.0_Hz
    - **components**:
      -
        - **name**: two_port_oscilloscope
        - **ports**:
          -
            - **name**: CH1
            - **parent_component_name**: None
          -
            - **name**: CH2
            - **parent_component_name**: None
        - **connections**: None
        - **components**:
      -
        - **name**: two_port_oscilloscope
        - **ports**:
          -
            - **name**: CH1
            - **parent_component_name**: None
        - **connections**: None
        - **components**:
      -
        - **name**: power_splitter_1to2
        - **ports**:
          -
            - **name**: IN
            - **parent_component_name**: None
          -
            - **name**: OUT1
            - **parent_component_name**: None
          -
            - **name**: OUT2
            - **parent_component_name**: None
        - **connections**: None
        - **components**:
    - **connections**:
      -
        - **name**: None
        - **ports**:
          -
            - **name**: OUT1
            - **parent_component_name**: None
          -
            - **name**: CH1
            - **parent_component_name**: None
      -
        - **name**: None
        - **ports**:
          -
            - **name**: OUT2
            - **parent_component_name**: None
          -
            - **name**: CH2
            - **parent_component_name**: None
    - **goal**: 
    - **parameters**:
      - **square_wave_frequency_Hz**: 10000000000.0
    - **index**: None
    - **date_configured**: 
    - **date_measured**: 
    - **measurement_configuration_list**:
- **parameters_list**:
  -
    - **square_wave_frequency_Hz**: 1000000000.0
  -
    - **square_wave_frequency_Hz**: 3000000000.0
  -
    - **square_wave_frequency_Hz**: 5000000000.0
  -
    - **square_wave_frequency_Hz**: 10000000000.0
- **parent_directory**: None
